# ADR 0003: Naming of Port Environment Variables

- **Status:** Accepted
- **Date:** August 2, 2026
- **Assigned to:** Jorge Armando Ceras Cárdenas - [armandx06](https://github.com/armandx06)

## Context and Problem Description

As part of the Dockerization of the API, the name of the `POSTGRES_HOST_PORT` environment variable does not clearly explain its actual purpose. This is because, within the Docker network (where the API will reside), the API does not use the host port but rather the internal network port.

## Factors Behind the Decision

The main factor driving this change is to keep the code readable and meaningful. Using a variable named for the host but used for the internal network creates a serious inconsistency.

## Options Considered

1. Rename the variable
2. Add a variable for the internal network

## Outcome of the decision

It was decided to use the second option, because renaming the variable would render it useless for configurations that are consistent with that naming convention, requiring manual updates wherever it was used. Furthermore, if the host’s port were to change, the entire code would have to be manually updated, whereas by adding a `POSTGRES_INTERNAL_PORT` variable, we maintain the global host port configuration and add the internal port layer.

### Implementation Details

For this implementation, simply:

1. Add the `POSTGRES_INTERNAL_PORT` variable to `.env` and update the variable in `apps/api/app/core/config.py` where it was previously used; simply replace the variable name with the new name to be used.
2. In Docker Compose `infra/docker/docker-compose.yml`, we adjust the use of variables in the db service so that the ports are retrieved from `.env`

```yml
ports:
  - ${POSTGRES_HOST_PORT}:${POSTGRES_INTERNAL_PORT}
```

And that’s all there is to the implementation. This is done solely to maintain consistency and, if necessary, to ensure that the API ports are managed in the same way.

## Consequences

This decision ensures better code readability and maintainability.

---

Created by [armandx06](https://github.com/armandx06) on August 2, 2026
