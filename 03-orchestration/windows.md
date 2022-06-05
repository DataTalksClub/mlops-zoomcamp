## Prefect on Windows

There is just a slight tweak to installation instructions if you are on Windows.

You will need to install 2.0b6 (to be released Monday June 7). 2.0b6 will officially support Windows. Use this instead of 2.0b5 shows in the lectures.

```
pip install prefect==2.0b6
```

Note that 2.0b5 and 2.0b6 are not compatible because 2.0b6 contains breaking changes. If you run into issues, you can reset the Prefect database by doing:

```
prefect orion database reset
```

This command will clear the data held by Orion.
