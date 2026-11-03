# Maltego Setup Guide for the Tomba Transforms

The full guide, with every transform and its options, is in the [README](../README.md).

## Quick setup

1. Clone the repository and install the dependencies (Python 3.10+):

    ```bash
    git clone https://github.com/tomba-io/tomba-maltego.git
    cd tomba-maltego
    pip install -r requirements.txt
    ```

2. Add your credentials from [app.tomba.io/api](https://app.tomba.io/api):

    ```bash
    cp settings.py.template settings.py
    # set TOMBA_API_KEY (ta_...) and TOMBA_SECRET_KEY (ts_...)
    ```

3. Download `tomba_transforms.mtz` from the [latest release](https://github.com/tomba-io/tomba-maltego/releases/latest).

4. In Maltego, choose **Import | Export > Import Config** and select `tomba_transforms.mtz`.

5. In **Transforms > Transform Manager**, set each Tomba transform's **Working directory** to your clone. The release file uses the placeholder `/path/to/tomba-maltego`. If you use a virtual environment, also set **Command line** to its Python.

## Check your setup

```bash
python3 test_setup.py                 # dependencies and credentials, no API request
python3 examples/test_transforms.py   # live: a free domain status check and one domain search
python3 project.py local emailcount stripe.com
```

## Troubleshooting

- **"Tomba API credentials are missing"**: create `settings.py`. Maltego doesn't pass shell environment variables to local transforms.
- **The transform fails to start**: the working directory or Python command in the transform settings is wrong. Fix them in the Transform Manager; the command line must be a Python that has the dependencies installed.
- **"Not enough Tomba credits" / "rate limit reached"**: see [Usage and quotas](https://docs.tomba.io/usage-and-quotas) and [Rate limits](https://docs.tomba.io/rate-limits).
