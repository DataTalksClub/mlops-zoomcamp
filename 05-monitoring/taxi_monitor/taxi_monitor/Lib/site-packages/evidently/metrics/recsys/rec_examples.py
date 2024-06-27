from functools import reduce
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import numpy as np
import pandas as pd

from evidently.base_metric import InputData
from evidently.base_metric import Metric
from evidently.base_metric import MetricResult
from evidently.calculations.recommender_systems import get_prediciton_name
from evidently.core import IncludeTags
from evidently.model.widget import BaseWidgetInfo
from evidently.options.base import AnyOptions
from evidently.pipeline.column_mapping import RecomType
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import ColumnDefinition
from evidently.renderers.html_widgets import RichTableDataRow
from evidently.renderers.html_widgets import RowDetails
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import rich_table_data
from evidently.renderers.html_widgets import table_data


class RecCasesTableResults(MetricResult):
    class Config:
        pd_include = False
        field_tags = {
            "user_ids": {IncludeTags.Extra},
            "current": {IncludeTags.Current, IncludeTags.Extra},
            "reference": {IncludeTags.Reference},
            "current_train": {IncludeTags.Current, IncludeTags.Extra},
            "reference_train": {IncludeTags.Reference},
        }

    user_ids: List[str]
    current: Dict[str, pd.DataFrame]
    current_train: Dict[str, List[str]] = {}
    reference: Dict[str, pd.DataFrame] = {}
    reference_train: Dict[str, List[str]] = {}


class RecCasesTable(Metric[RecCasesTableResults]):
    user_ids: Optional[List[Union[int, str]]]
    display_features: Optional[List[str]]
    item_num: Optional[int]
    train_item_num: int

    def __init__(
        self,
        user_ids: Optional[List[Union[int, str]]] = None,
        display_features: Optional[List[str]] = None,
        train_item_num: int = 10,
        item_num: Optional[int] = None,
        options: AnyOptions = None,
    ) -> None:
        self.user_ids = user_ids
        self.display_features = display_features
        self.item_num = item_num
        self.train_item_num = train_item_num
        super().__init__(options=options)

    def calculate(self, data: InputData) -> RecCasesTableResults:
        curr = data.current_data
        ref = data.reference_data
        datetime_column = data.data_definition.get_datetime_column()
        prediction_name = get_prediciton_name(data)
        recommendations_type = data.column_mapping.recom_type
        user_id_column = data.data_definition.get_user_id_column()
        item_id_column = data.data_definition.get_item_id_column()
        current_train_data = data.additional_data.get("current_train_data")
        reference_train_data = data.additional_data.get("reference_train_data")
        current_train = {}
        display_features = self.display_features if self.display_features is not None else []

        if recommendations_type is None or user_id_column is None or item_id_column is None:
            raise ValueError("recommendations_type, user_id, item_id must be provided in the column mapping.")

        user_id = user_id_column.column_name
        item_id = item_id_column.column_name

        user_ids = self.user_ids
        if user_ids is None:
            if current_train_data is not None:
                if ref is not None:
                    user_ids = list(
                        reduce(np.intersect1d, (curr[user_id], current_train_data[user_id], ref[user_id]))[:5]
                    )
                else:
                    user_ids = list(np.intersect1d(curr[user_id], current_train_data[user_id])[:5])
            if user_ids is None or len(user_ids) == 0:
                user_ids = list(curr[user_id].unique()[:5])

        if current_train_data is not None:
            if datetime_column is not None:
                current_train_data = current_train_data.sort_values(datetime_column.column_name)
            for user in user_ids:
                user_df = current_train_data[current_train_data[user_id] == user]
                res = user_df[-min(self.train_item_num, user_df.shape[0]) :][item_id].astype(str)
                current_train[str(user)] = list(res)
        current = {}
        if recommendations_type == RecomType.RANK:
            ascending = True
        else:
            ascending = False
        curr = curr.sort_values(prediction_name, ascending=ascending)
        for user in user_ids:
            res = curr.loc[curr[user_id] == user, [prediction_name, item_id] + display_features].astype(str)
            if self.item_num is not None:
                res = res[: self.item_num]
            current[str(user)] = res

        reference = {}
        reference_train = {}
        if ref is not None:
            ref = ref.sort_values(prediction_name, ascending=ascending)
            for user in user_ids:
                res = ref.loc[ref[user_id] == user, [prediction_name, item_id] + display_features].astype(str)
                if self.item_num is not None:
                    res = res[: self.item_num]
                reference[str(user)] = res
            if reference_train_data is not None:
                if datetime_column is not None:
                    reference_train_data = reference_train_data.sort_values(datetime_column.column_name)
                for user in user_ids:
                    user_df = reference_train_data[reference_train_data[user_id] == user]
                    res = user_df[-min(self.train_item_num, user_df.shape[0]) :][item_id].astype(str)
                    reference_train[str(user)] = list(res)
        return RecCasesTableResults(
            user_ids=[str(x) for x in user_ids],
            current=current,
            current_train=current_train,
            reference=reference,
            reference_train=reference_train,
        )


@default_renderer(wrap_type=RecCasesTable)
class RecCasesTableRenderer(MetricRenderer):
    def _generate_user_params(self, user_id, curr_user_train, curr_user_rec, ref_user_train, ref_user_rec):
        details = RowDetails()
        curr_title = ""
        ref_title = ""
        if curr_user_train is not None:
            curr_title = "Previous interactions: " + ", ".join(curr_user_train)
        if ref_user_train is not None:
            ref_title = "Previous interactions: " + ", ".join(ref_user_train)
        if curr_title != "" and ref_user_train is None:
            ref_title = curr_title
        curr = table_data(
            title=curr_title,
            column_names=curr_user_rec.columns,
            data=curr_user_rec.values,
        )
        details.with_part("current", info=curr)
        if ref_user_rec is not None:
            ref = table_data(
                title=ref_title,
                column_names=ref_user_rec.columns,
                data=ref_user_rec.values,
            )
            details.with_part("reference", info=ref)

        fields = {
            "user_id": user_id,
        }
        return RichTableDataRow(details=details, fields=fields)

    def render_html(self, obj: RecCasesTable) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        user_ids = results.user_ids
        params_data = []

        for user_id in user_ids:
            user_params = self._generate_user_params(
                user_id,
                results.current_train.get(user_id),
                results.current.get(user_id),
                results.reference_train.get(user_id),
                results.reference.get(user_id),
            )
            params_data.append(user_params)
        table_columns = [ColumnDefinition("User_id", "user_id")]

        return [
            header_text(label="Recommendation Cases Table"),
            rich_table_data(
                title="",
                columns=table_columns,
                data=params_data,
            ),
        ]
