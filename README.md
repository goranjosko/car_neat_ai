# car_neat_ai
Training car agents to drive, stop at red lights, etc. with the help of NEAT AI

This is a hobby project in development, for now it is possible to train the car to stay in the middle of the road while driving, stop when it senses a red light and choose a turn. 
 - The car sees the world through a series of rays that are fired from a certain place on the front of the car.
 - In addition the car senses the surface it is driving on, if the surface is red the car will automatically increase the value of one of the inputs and thus stop the vehicle until the red light disappears (because is trained that way). 
 - In a similar way, the car chooses the first left or right turn, depending on the value of one input selected for that purpose.
