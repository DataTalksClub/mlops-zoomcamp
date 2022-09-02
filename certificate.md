## Getting your certificate

Congratulations on finishing the course!

Here's how you can get your certificate.

First, get your certificate id using the `compute_certificate_id` function:

```python
from hashlib import sha1

def compute_hash(email):
    return sha1(email.encode('utf-8')).hexdigest()

def compute_certificate_id(email):
    email_clean = email.lower().strip()
    return compute_hash(email_clean + '_')
```

Then use this hash to get the URL

```python
cohort = 2022
course = 'mlops-zoomcamp'
your_id = compute_certificate_id('never.give.up@gmail.com')
url = f"https://certificate.datatalks.club/{course}/{cohort}/{your_id}.pdf"
print(url)
```

Example: https://certificate.datatalks.club/mlops-zoomcamp/2022/fe629854d45c559e9c10b3b8458ea392fdeb68a9.pdf
