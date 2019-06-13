# renew-cert

Docker image using certbot with dns-route53 plugin to generate a
certificate via [Let's Encrypt](https://letsencrypt.org/) and store
the contents in SSM Parameter Store.

## Usage

```bash
# Use make to build and run after checking out the project
# Requires valid credentials in ~/.aws
email=my.email@my.domain.org domain=my.domain.org region=us-east-1 make run

# Run with docker
docker run --rm \
    -e EMAIL=my.email@my.domain.org \
    -e DOMAIN=my.domain.org \
    -e AWS_REGION=us-east-1 \
    sgdan/renew-cert
```

Commands above will create SecureString values in SSM Parameter Store under these paths:

- `/cert/my.domain.org/chain`
- `/cert/my.domain.org/key`

Wildcard domains like `*.domain.org` will be replaced with underscore
e.g. `/cert/_.domain.org/chain`
