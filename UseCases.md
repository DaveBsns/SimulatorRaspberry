# Use Cases Bicycle Simulator

## Use Case Overview

R1 - Removing barriers and building security

R2 - Expansion of driving practice (mainly on intersections)

R3 - Expansion of driving practice (mainly overtaking and narrow spots)

R4 - Expansion of driving practice at different times of the day

R5 - Weather influences when cycling

A1 - Building confidence on the bicycle path next to the road

A2 - Building confidence when driving on the road

A3.1 - Feeling safe when being overtaken by cars

A3.2 - Measuring stress when being overtaken by cars

A4 - Cycling at night and sharing the road with other cars

A5 - Cycling under varying weather conditions at varying times of day and at night

The individual cyclist actions are taken from the requirements document and named in alphabetical order.

## Use Case R1 - Removing barriers and building security

| Use Case Number | Description                                                                 | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | --------------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| R1a             | Getting on the bike                                                         | 1        |        | x            |       |       |
| R1b             | Starting to ride the bike straight on even ground, no vehicles driving past | 1        | x      |              |       |       |
| R1b             | Raising the right hand to indicate an upcoming turn to the right            | 1        | x      | x            |       |       |
| R1b             | Turning right                                                               | 1        | x      | x            |       |       |
| R1c             | Raising the left hand to indicate an upcoming turn to the right             | 2        | x      | x            |       |       |
| R1c             | Turning left                                                                | 2        | x      | x            |       |       |
| R1d             | Driving uphill                                                              | 4        | x      |              |       | x     |
| R1d             | Driving downhill                                                            | 4        | x      |              | (x)   | x     |
| R1e             | Riding around obstacle on the floor                                         | 3        | x      | x            |       |       |
| R1f             | Hitting the brakes hard because of a dangerous situation                    | 3        |        |              | x     |       |

## Use Case R2 - Expansion of driving practice (mainly on intersections)

| Use Case Number | Description                                                       | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ----------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| R2a             | Cyclist starts riding at an intersection                          | 1        | x      |              |       |       |
| R2b             | Cyclist stops for a red traffic light                             | 1        |        |              | x     |       |
| R2c             | Right turn indication and execution at an intersection            | 1        | x      | x            |       |       |
| R2c             | Left turn indication and execution at an intersection             | 2        | x      | x            |       |       |
| R2d             | Getting into the turning lane                                     | 2        | x      | x            | x     |       |
| R2e             | Traffic signs at intersections: Stop, Vorfahrt, Vorfahrt gewähren | 1/2/3    | x      |              | x     |       |

##

## Use Case R3 - Expansion of driving practice (mainly overtaking and narrow spots)

| Use Case Number | Description                                                       | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ----------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| R3a             | Driving past parked car (regular parking)                         | 1        | x      |              |       |       |
| R3a             | Driving past parked car (bad parking going into the bicycle lane) | 2        |        |              | x     |       |
| R3b             | Overtaking other cyclists                                         | 3        | x      | x            |       |       |
| R3c             | Driving through a narrow point                                    | 3        | x      | (x)          | (x)   |       |

## Use Case R4 - Expansion of driving practice at different times of the day

| Use Case Number | Description              | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ------------------------ | -------- | ------ | ------------ | ----- | ----- |
| R4a             | Driving at dusk          | 2        | x      |              |       |       |
| R4b             | Driving during the night | 3        | x      |              |       |       |

## Use Case R5 - Weather influences when cycling

| Use Case Number | Description                                                                 | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | --------------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| R5a             | Driving on wet road                                                         | 3        | x      |              |       |       |
| R5b             | Driving in rain                                                             | 3        | x      |              |       |       |
| R5b             | Driving in fog                                                              | 4        | x      |              |       |       |
| R5c             | Driving in snow and slippery conditions                                     | 4        | x      | x            |       |       |
| R5c             | Driving in snow and slippery conditions on a bridge                         | 4        | x      | x            |       |       |
| R5d             | Braking for an obstacle visible only late because of bad weather conditions | 4        |        |              | x     |       |
| R5d             | Braking in slippery weather conditions                                      | 4        |        | x            | x     |       |
| R5e             | Driving at night —> see no difference to R4b                                | 3        | x      |              |       |       |
| R5f             | Driving in the city with poor visibility                                    | 3        | x      |              |       |       |
| R5f             | Driving in the forest with poor visibility                                  | 4        | x      |              |       |       |

## Use Case A1 - Building confidence on the bicycle path next to the road

| Use Case Number | Description                                                                  | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ---------------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| A1a             | Being overtaken by passing cars in low traffic density                       | 1        | x      |              |       |       |
| A1a             | Being overtaken by passing cars in high traffic density                      | 2        | x      |              |       |       |
| A1b             | Being overtaken by passing cars with low speed                               | 1        | x      |              |       |       |
| A1b             | Being overtaken by passing cars with high speed                              | 2        | x      |              |       |       |
| A1c             | Crossing an intersection with low traffic density and traffic lights         | 1        | x      |              | x     |       |
| A1c             | Crossing an intersection with high traffic density and regular road crossing | 2        | x      |              | x     |       |

##

## A2 - Building confidence when driving on the road

| Use Case Number | Description                                                          | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | -------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| A2a             | Driving on the road, no bike path, low traffic density, slow cars    | 1        | x      |              |       |       |
| A2a             | Driving on the road, no bike path, high traffic density, fast cars   | 2        | x      |              |       |       |
| A2bde           | Approaching an intersection with cars, right turn incl. turning lane | 1        | x      | x            | x     |       |
| A2bde           | Approaching an intersection with cars, left turn incl. turning lane  | 2        | x      | x            | x     |       |
| A2c             | Stopping at traffic lights                                           | 1        |        |              | x     |       |

##

## A3.1 - Feeling safe when being overtaken by cars

| Use Case Number | Description                                              | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | -------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| A3a             | Being overtaken by a car with usual distance             | 1        | x      |              |       |       |
| A3a             | Being overtaken by a close car                           | 2        | x      |              |       |       |
| A3b             | Being overtaken by a slow car (combine with A2a)         | 1        | x      |              |       |       |
| A3b             | Being overtaken by a fast car (combine with A2a)         | 2        | x      |              |       |       |
| A3c             | Being overtaken by a fast car with obstacles on the side | 2        | x      |              | x     |       |

##

## A4 - Cycling at night and sharing the road with other cars

| Use Case Number | Description                                                            | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ---------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| A4a             | Driving at dusk with car headlights behind you or in oncoming traffic  | 2        | x      |              |       |       |
| A4b             | Driving at night with car headlights behind you or in oncoming traffic | 3        | x      |              |       |       |

##

## A5 - Cycling under varying weather conditions at varying times of day and at night

| Use Case Number | Description                                                            | Scenario | Direto | Rocker Plate | Brake | Rizer |
| --------------- | ---------------------------------------------------------------------- | -------- | ------ | ------------ | ----- | ----- |
| A5a             | Driving on a wet road with cars next to it                             | 3        | x      |              |       |       |
| A5b             | Driving in rain/fog or poor visibility including car headlights        | 3        | x      |              |       |       |
| A5c             | Driving in snow and slippery conditions, possibly with splashing slush | 3        | x      |              |       |       |
| A5d             | Driving in different weather conditions at dusk and at night           | 2        | x      |              |       |       |
