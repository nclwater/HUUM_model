# README

This package contains the Household Utility Usage Model HUUM.
It is an agent based modelling system, which is optimised to represent any utility usage in a household.
While models can be defined in code, it is recommended to define them in data, using the [HUUM_io](https://github.com/nclwater/HUUM_io) package.
Neither is uploaded to the general Python package server, so a manual, local install is necessary.

The documentation of the concepts and the logic in this program can be found in the thesis _Agent Based Modelling of city-wide Water Demand_ (not yet published).

Created by Sven Berendsen as part of his PhD project at Newcastle University, (C) 2023.
Licenced under the terms of the Apache License 2.0.

## ToDo
Additional, smaller todo's are noted in each individual file.
Bigger ones are:

- Professionalise Code: Currently the code is "clean prototype" level, i.e. has little in-code documentation (but very sensible function and object names). Also missing are asserts and unit tests.
- Switch to kwargs as arguments where appropiate. This most likely is best for event execution.
- Implement consistency checks before model initialisation.
- Implement all event hooks and possible effects.
- Introduce an element to use externally set time series.
- Convert the current agent -> appliance interaction into an agent -> action -> appliance interaction, enabling more flexibility in representing agent actions.
- Switch to using class-method decorators for more concise code.
- Re-implement in another language, e.g. Julia or Rust, for performance reasons.
- Parallelise to improve large model runtime.

## Licence
This code is originally (C) Sven Berendsen, 2023.
Published under the terms of the Apache Licence, version 2.0.
