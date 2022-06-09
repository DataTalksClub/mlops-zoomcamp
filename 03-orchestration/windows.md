## Prefect on Windows

If you use WSL, you should have no problems running Prefect Orion.

But if you aren't, there is just a slight tweak to installation instructions if you are on Windows.

You will need to install 2.0b6 (to be released Monday June 7). 2.0b6 will officially support Windows. Use this instead of 2.0b5 shows in the lectures.

```
pip install prefect==2.0b6
```

Note that 2.0b5 and 2.0b6 are not compatible because 2.0b6 contains breaking changes. If you run into issues, you can reset the Prefect database by doing:

```
prefect orion database reset
```

This command will clear the data held by Orion.

### Docker

You can also try running Prefect in Docker. For example:

```
docker run -it --rm \
    -p 4200:4200 \
    prefecthq/prefect:2.0b5-python3.8 \
        prefect orion start --host=0.0.0.0
```

and then view it from `localhost:4200`.

### Prefect Cloud

You can also just use Cloud so you don't have to host Prefect Orion yourself. Instructions can be found here:

https://orion-docs.prefect.io/ui/cloud-getting-started/
