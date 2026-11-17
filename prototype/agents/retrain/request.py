"""Publie une demande de réentraînement à la main, pour tester sans l'orchestrateur.

    python -m agents.retrain.request --start 2023-02
    python -m agents.retrain.request --start 2023-01 --end 2023-03 --by ismail --approved-by responsable
"""
import argparse

from common.events import Event, EventBus, EventType

parser = argparse.ArgumentParser(description="Envoie un événement retrain_requested.")
parser.add_argument("--start", required=True, help="premier mois, ex. 2023-02")
parser.add_argument("--end", help="dernier mois (par défaut : --start)")
parser.add_argument("--by", default="humain", help="qui demande")
parser.add_argument("--approved-by", help="qui a validé (scénario 3)")
args = parser.parse_args()

event = Event(
    type=EventType.RETRAIN_REQUESTED,
    source="humain",
    payload={
        "period": {"start": args.start, "end": args.end or args.start},
        "requested_by": args.by,
        "approved_by": args.approved_by,
    },
)
EventBus().publish(event)
print("Envoyé :", event.to_json())