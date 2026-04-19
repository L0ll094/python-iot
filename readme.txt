# Making a fake IoT Device to practice AWS IoT tools.


Topics structure are governed by Sparkplug - B
Update your policy resources to cover both prefixes: topic/d2c/* and topicfilter/c2d/* in addition to the connect block.

    Copy of ridiculously permissive policy 
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
      "Resource": "arn:aws:iot:eu-north-1:169024356372:topic/spBv1.0/NextGen/*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Subscribe",
      "Resource": "arn:aws:iot:eu-north-1:169024356372:topicfilter/spBv1.0/NextGen/*"
    },
    {
      "Effect": "Allow",
      "Action": "iot:Connect",
      "Resource": "arn:aws:iot:eu-north-1:169024356372:client/*"
    }
  ]
}