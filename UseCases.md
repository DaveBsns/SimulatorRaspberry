# Use Cases Bicycle Simulator

## Use Case Overview
R1 - Removing Barries and building security

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

## Use Case R1 - Removing Barries and building security
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  R1a<br/> | Getting on the bike<br/> | 1<br/> |  | x<br/> |  |  |
|  R1b<br/> | Starting to ride the bike straight on even ground, no vehicles driving past <br/> | 1<br/> | x<br/> |  |  |  |
|  R1b<br/> | Raising the right hand to indicate an upcoming turn to the right<br/> | 1<br/> | x<br/> | x<br/> |  |  |
|  R1b<br/> | Turning right —> right turns have no danger of being hit by a vehicle overtaking the cyclist, hence this comes first<br/> | 1<br/> | x<br/> | x<br/> |  |  |
|  R1c<br/> | Raising the left hand to indicate an upcoming turn to the right<br/> | 2<br/> | x<br/> | x<br/> |  |  |
|  R1c<br/> | Turning left<br/> | 2<br/> | x<br/> | x<br/> |  |  |
|  R1d<br/> | Driving uphill<br/> | 4<br/> | x<br/> |  |  | x<br/> |
|  R1d<br/> | Driving downhill<br/> | 4<br/> | x<br/> |  | (x)<br/> | x<br/> |
|  R1e<br/> | Riding around obstacle on the floor<br/> | 3<br/> | x<br/> | x<br/> |  |  |
|  R1f<br/> | Hitting the brakes hard because of a dangerous situation<br/> | 3<br/> |  | x(?)<br/> | x<br/> |  |

## Use Case R2 - Expansion of driving practice (mainly on intersections)
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  R2a<br/> | Cyclist starts riding at an intersection<br/> | 1<br/> | x<br/> |  |  |  |
|  R2b<br/> | Cyclist stops for a red traffic light<br/> | 1<br/> |  |  | x<br/> |  |
|  R2c<br/> | Right turn indication and execution at an intersection<br/> | 1<br/> | x<br/> | x<br/> |  |  |
|  R2c<br/> | Left turn indication and execution at an intersection<br/> | 2<br/> | x<br/> | x<br/> |  |  |
|  R2d<br/> | Getting into the turning lane —> this should be implemented along with R2c imo<br/> | 2<br/> | x<br/> | x<br/> | x<br/> |  |
|  R2e<br/> | Traffic signs at intersections: Stop, Vorfahrt, Vorfahrt gewähren<br/> | 1/2/3<br/> | x (depends on the traffic sign)<br/> |  | x (depends on the traffic sign)<br/> |  |

## 

## Use Case R3 - Expansion of driving practice (mainly overtaking and narrow spots)
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  R3a<br/> | Driving past parked car (regular parking)<br/> | 1<br/> | x<br/> |  |  |  |
|  R3a<br/> | Driving past parked car (bad parking going into the bicycle lane)<br/> | 2<br/> |  |  | x<br/> |  |
|  R3b<br/> | Overtaking other cyclists<br/> | 2<br/> | x<br/> | x<br/> |  |  |
|  R3c<br/> | Driving through a narrow point<br/> | 3<br/> | x<br/> | (x)<br/> | (x)<br/> |  |

## Use Case R4 - Expansion of driving practice at different times of the day
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  R4a<br/> | Driving at dusk<br/> | 2<br/> | x<br/> |  |  |  |
|  R4b<br/> | Driving during the night<br/> | 3<br/> | x<br/> |  |  |  |

## Use Case R5 - Weather influences when cycling
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  R5a<br/> | Driving on wet road<br/> | 2<br/> | x<br/> |  |  |  |
|  R5b<br/> | Driving in rain<br/> | 2<br/> | x<br/> |  |  |  |
|  R5b<br/> | Driving in fog<br/> | 3<br/> | x<br/> |  |  |  |
|  R5c<br/> | Driving in snow and slippery conditions<br/> | 3<br/> | x<br/> | x<br/> |  |  |
|  R5c<br/> | Driving in snow and slippery conditions on a bridge<br/> | 3<br/> | x<br/> | x<br/> |  |  |
|  R5d<br/> | Braking for an obstacle visible only late because of bad weather conditions (combine with R1f)<br/> | 3<br/> |  |  | x<br/> |  |
|  R5d<br/> | Braking in slippery weather conditions<br/> | 3<br/> |  | x<br/> | x<br/> |  |
|  R5e<br/> | Driving at night —> see no difference to R4b<br/> | 3<br/> | x<br/> |  |  |  |
|  R5f<br/> | Driving in the city with poor visibility —> combine with R5b and pretty much any other use case<br/> | 3<br/> | x<br/> |  |  |  |
|  R5f<br/> | Driving in the forest with poor visibility —> combine with R5b<br/> | 4<br/> | x<br/> |  |  |  |

## Use Case A1 - Building confidence on the bicycle path next to the road
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  A1a<br/> | Being overtaken by passing cars in low traffic density<br/> | 1<br/> | x<br/> |  |  |  |
|  A1a<br/> | Being overtaken by passing cars in high traffic density<br/> | 2<br/> | x<br/> |  |  |  |
|  A1b<br/> | Being overtaken by passing cars with low speed<br/> | 1<br/> | x<br/> |  |  |  |
|  A1b<br/> | Being overtaken by passing cars with high speed<br/> | 2<br/> | x<br/> |  |  |  |
|  A1c<br/> | Crossing an intersection with low traffic density and traffic lights<br/> | 1<br/> | x<br/> |  | x<br/> |  |
|  A1c<br/> | Crossing an intersection with high traffic density and regular road crossing (Zebrastreifen)<br/> | 2<br/> | x<br/> |  | x<br/> |  |

## 

## A2 - Building confidence when driving on the road
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  A2a<br/> | Driving on the road without a bike path with low traffic density<br/>and slow cars<br/> | 1<br/> | x<br/> |  |  |  |
|  A2a<br/> | Driving on the road without a bike path with high traffic density and fast cars<br/> | 2<br/> | x<br/> |  |  |  |
|  A2bde<br/> | Approaching an intersection with cars, right turn incl. turning lane<br/> | 1<br/> | x<br/> | x<br/> | x<br/> |  |
|  A2bde<br/> | Approaching an intersection with cars, left turn incl. turning lane<br/> | 2<br/> | x<br/> | x<br/> | x<br/> |  |
|  A2c<br/> | Stopping at traffic lights<br/> | 1<br/> |  |  | x<br/> |  |

## 

## A3.1 - Feeling safe when being overtaken by cars
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  A3a<br/> | Being overtaken by a car with usual distance<br/> | 1<br/> | x<br/> |  |  |  |
|  A3a<br/> | Being overtaken by a close car<br/> | 2<br/> | x<br/> |  |  |  |
|  A3b<br/> | Being overtaken by a slow car (combine with A2a)<br/> | 1<br/> | x<br/> |  |  |  |
|  A3b<br/> | Being overtaken by a fast car (combine with A2a)<br/> | 2<br/> | x<br/> |  |  |  |
|  A3c<br/> | Being overtaken by a fast car with obstacles on the side<br/> | 2<br/> | x<br/> |  | x<br/> |  |

## 

## A4 - Cycling at night and sharing the road with other cars
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  A4a<br/> | Driving at dusk with car headlights behind you or in oncoming traffic<br/> | 2<br/> | x<br/> |  |  |  |
|  A4b<br/> | Driving at night with car headlights behind you or in oncoming traffic<br/> | 3<br/> | x<br/> |  |  |  |

## 

## A5 - Cycling under varying weather conditions at varying times of day and at night
|  Use Case Number<br/> | Description<br/> | Scenario<br/> | Pedal sensor aka. Direto Trainer<br/> | Rocker Plate sensors<br/> | Brake sensor<br/> | Rizer<br/> |
|-----|-----|-----|-----|-----|-----|-----|
|  A5a<br/> | Driving on a wet road with cars next to it (combine with R5a)<br/> | 2<br/> | x<br/> |  |  |  |
|  A5b<br/> | Driving in rain/fog or poor visibility including car headlights (combine with R5b)<br/> | 3<br/> | x<br/> |  |  |  |
|  A5c<br/> | Driving in snow and slippery conditions, possibly with splashing slush<br/> | 3<br/> | x<br/> |  |  |  |
|  A5d<br/> | Driving in different weather conditions at dusk and at night (combine with A4a, R4b…)<br/> | 2<br/> | x<br/> |  |  |  |

