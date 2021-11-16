# Notes
## Bridge duties
### Image recognition
We're going to take care of the image recognition part to recognize customers and estimated sex, age etc... locally, for the following reasons:
- Images of people are not going to the cloud => better privacy
- The bridge is already taking care of processing the raw datas, so that only clean an ready to use datas are sent to the cloud
- We are selling more expensive hardware to the customers instead of paying higher amounts of money on the server subscription

## TODO:
- [ ] Finding a good library for people recognition
- [ ] Do we have a camera? (check rasperry camera)
- [ ] What datas we need to actually extract from the image recognition
- [ ] should the camera be in the same device as the bridge
- [ ] do we need to have two different code files for the bridge and the microcontroller?
- [ ] can an Arduino recognize images? or how do we make the microcontroller recognize the images (having two seperate programms run on the microcontroller part?)
- [ ] Check how to save the datas to the DB (group data by message from bridge to cloud => message_id)
- [ ] Web interface

## Protocol Arduino - Bridge
[FF] [Sensor ID] [Data type] [Data size] [Data] [FE]
- in the bridge there should be some kind of dictionary that converts the Sensor ID to the actual sensor to understand what data we get

## Data Model (Protocol Bridge - Cloud)
```json
{
  "bridge_id" : number,
  "Data type" : string,
  "Value" : [number, ],
}
```

## Sensor/actuators types
#### Sensors
- Temperature
- Light
- People
  - Age
  - Sex
  - Groups

#### Actuators
- Light color
- Music
- Perfume
- Brightness
- Temeprature
- ADs display
  - Best offerts
  - Group offerts

## Cloud
- Subscribe a bridge
- Post stuff
- Get stuff

# IF WE HAVE TIME
- [ ] Basic web interface to manage bridge sensors/actuator
- [ ] Telegram bot
- [ ] who is inside the shop (all the people)
- [ ] the AI in the cloud should somehow get feedback on wether or not the decision that it took in the past was good or not
- [ ] a shop with multiple rooms

## Things to ask the lecturer:
 - [ ] Camera cable
