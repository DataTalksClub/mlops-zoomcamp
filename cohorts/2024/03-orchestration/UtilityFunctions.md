# Utility Functions, Why and How to use them Effectively in a Project
A utility function in Python is a **small, self-contained piece of code that performs a specific task**. It's called a "utility" because it's a helpful tool that makes a certain task easier to perform. These functions are not meant to be standalone, but rather to be used in conjunction with other code.

## Why use utility functions
### Code Reusability
If you find yourself having to often recycle the same lines of code again and again. It is far more streamlined to have a function at the top of your script or a completely separate utilities script. So for example instead of having to call two functions to extract the mean and median simply create a single function `get_mean_median` and call this whenever you need to return both the mean and median

```
def get_mean_median(list):
    mean = np.mean(list)
    median = np.median(list)
    return mean, median
```
Not only does this reduce code duplication but it also helps the code to be more maintainable.

### Modularisation and Organisation
Separating utility functions into their own modules or packages helps organise everything into clear blocks which can then be worked on, and if any bugs appear they are easier to locate. All in all this makes the code easier to understand, maintain, and extend.

### Abstraction and Encapsulation
Instead of groaning when you see a 10,000+ line long script. Having utility functions can provide a "higher level abstraction", or in plain English it is easier to work out what the code is trying to achieve and how it is doing it.

### Testability
By having separate utility functions, it becomes much easier to write unit tests.

### Re-use
Often utility functions can be re-used in other projects. Having them stored as a utility function rather than nested in each script. For example, when in academia I had a utility function to produce a custom boxplot with all the individual points overlaid. This ensured that for all my published papers my figures would look the same.

## Best Practices
### Naming Conventions
This can be a little controversial as not everyone has the same standards (like like in pandas dataframe column names). But here are my general tips for all functions

#### Lowercase and underscores for function names
Unless unavoidable avoid using any capitalisation and hyphens in naming your function. This helps you identify what functions looklike. Personally this is how I devise my conventions

|   | Functions | Function Parameters | Variables | Constants | Classes |
|---|-----------|---------------------|-----------|-----------|---------|
| Convention | Lowercase and underscores | Lowercase and underscores | lowercase and hyphens | Allcaps and underscores| CamelCase |
|Example | get_basic_stats() | alpha_val | gp1-mean | EXPORT_PATH | RandomForestClassifier

*NB Stating the obvious, don't use single letters. No-one will know what they stand for.*

#### Start with a verb
Start your function with a verb. This helps others understand what your function is without having to trawl through documentation. This verb should clearly describe the function's purpose or action. This helps others if they want to use the functions and know which one they need to use without having to trawl through the documentation.

Good function names examples are: `calculate_mean`, `preprocess_data`, `get_eval_metrics`.

#### For bespoke or trial functions add a suffix
Sometimes you may want to create a function that will conflict with a global function. What I suggest to do is add a suffix to the function with either your initials or the name of the project. For example, `get_mean_mnl()`. This helps by letting you know who created it or which project it is associated with (and no I'm not saying what the N stands for).

One use case for this is when you are evaluating the efficacy of two different approaches in a prototype. By attaching the suffix it is clear the two functions are related but distinct and they can be called in a similar manner.

By why suffixes and not prefixes? This is more of a preference rather than a hard-written rule, but it helps with auto-complete if you have either: lots of bespoke functions or several functions that do similar things. By putting the suffix last your presented options will limited to similar functions.

Also don't use versions as suffixes. After a while no-one will remember what the difference is between v3 and v4, and no-one is going to be using v1. Git is for versioning.

This is primarily useful for personal or project-specific finctions that aren't intended for widespread use. For open-source or shared libraries, use descriptive names that are more specific.

#### Stick to English
Unless your entire team speaks and operates in a different language *(and will remain doing so in the future)* stick to using English. This will make your code accessible to more people in the future. Especially if someone else is using it, or god-forbid, debugging it,  in the future.

### Write Docstrings
Nearly everyone who does programming hates writing documentation. It is often done at the end of a project and you've forgotten what things do. Don't be that person!

For short simple trivial functions there's no need but otherwise write the docstring once you've complteted the function or as you go along. Make sure to describe the inputs, and outputs alongside what the function does.

VSCode has extensions such as [autodocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) for free which can help you as you go along. Paid options such as [GitHub Copilot](https://docs.github.com/en/copilot) are also able to do this.

### Standardise File structures
Keep your code organised and easy to navigate for others. The most common approach is to create a folder for `utils`, and separate file(s) to create utilities and helper functions that can be grouped together.

Additionally create a `__init__.py` file in the `utils` directory. An `__init__.py` file instructs Python to treat this directory as a python package. [GeeksForGeeks](https://www.geeksforgeeks.org/what-is-__init__-py-file-in-python/) have quite a nice description for how `__init__.py` files work.

### Unit test your functions
Always test your functions, either by providing `unittests`, or by using `assert`. Dataquest have a good succinct guide [here](https://www.dataquest.io/blog/unit-tests-python/) which I recommend reading.

## An Example
For a working example I was creating a data loading model training pipeline for an MLOps course. Where I often had to perform a complex set of functions. I this case I constructed a utils folder with additional subfolders to further subdivide my functions (just remember to place the `__init__.py` each time). It looked similar to the structure below.

```
mlops_course
|── data_prep
|── training
|── evaluation
|── utils
    |── __init__.py
    |── analytics
        |── __init__.py
        |── data.py
    |── data_prep
        |── __init__.py
        |── cleaning.py
        |── encoders.py
        |── feature_engineering.py
        |── feature_selector.py
        |── splitters.py
    |── hyperparameters
        |── __init__.py
        |── shared.py
    |── models
        |── __init__.py
        |── sklearn.py
        |── xgboost.py
```

From here whenever I needed to access a particular utility function I can simply call in another script in the project. Say for example I want to dictionary vectorise my categorical features I simply import my `vectorise_features` function from my encoders.py utility file.

```
from mlops_course.utils.data_prep.encoders import vectorise_features

df_train, df_val = load_data()
X_train, X_val, dv = vectorise_features(df_train, df_val)
```

## Final Thoughts
As a self-trained coder, and particularly one who came from an academic MATLAB background I've always learnt as I've gone along which less help and guides that are now available in the python community. This meant making tons of mistakes, and having a very weighty and disorganised code base which didn't help when others needed to use my code. While I'm sure I've improved, I'm sure there are mistakes or other best practices for utility functions that I've missed. If that's the case do let me know. To be honest writing these down helps me in clarifying my thoughts and structures.

## Resources
* [autodocstring fo VS Code](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
* [GitHub Co-pilot Documentation](https://docs.github.com/en/copilot)
* [GeeksForGeeks - What is __Init__.Py File in Python?](https://www.geeksforgeeks.org/what-is-__init__-py-file-in-python/)
* [Dataquest - Unit Tests in Python](https://www.dataquest.io/blog/unit-tests-python/)