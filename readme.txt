# Making a fake IoT Device to practice AWS IoT tools.


## Explanation about the program for myself

To use this with the temperature sensor example:

1. Inside main() you define the connection details — broker address, port, and certificate paths — all from AWS IoT.

2. Next, create a TemperatureSensor instance, passing the device ID and connection config.

3. On the sensor, call run(). Inside run():
    1 Connect to the broker (self.connect()) — this sets up TLS, opens the connection, 
    starts the background network loop, and waits up to 5 seconds for confirmation, setting the is_connected when successful
    2 Subscribe to the topic to listen for incoming messages
    3 Loop 10 times: build a DeviceMessage, publish it, then wait 10 seconds

On AWS IoT Side
- Find your domain configuration name, this is your broker connection string 
- Create a thing. The thing name should be set to the same as the device_id of your device
- Create a certificate. Since this code just have 1 thing go ahead and make it exclusive
- Download all parts of the certificate into your defined spots where code says it's found
- Create a policy. The policy says what can happen on each topic, not who can do it. 
    Publish and recieve (and publishRetain if applicable)
    Here we define that for broker ARNBLABLA on topic devices/* we allow publishing and reciving

    Subscribe
    Here we define that it's allowed to subscribe to the topicfilter devices/*

    Connect
    Here we define that the specific action of IoT Connect is permitted for all clients
    A client is an IoT Device so if we only want my temp sensor "MySensor" to connect we can define that here."

At this stage everything happens on one topic, but will differentiate command topics soon

    Copy of very permissive policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Receive",
        "iot:PublishRetain"
      ],
      "Resource": [
        "arn:aws:iot:eu-north-1:169024356372:topic/devices/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": [
        "arn:aws:iot:eu-north-1:169024356372:topicfilter/devices/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": [
        "arn:aws:iot:eu-north-1:169024356372:client/*"
      ]
    }
  ]
}