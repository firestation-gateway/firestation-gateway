# Firestation Gateway

The Firestation Gateway application is used to detect events and respond to them.

The architecture is based on the producer and consumer model.

Each consumer can respond to one or more events. For example, when a smoke detector system is active (**generic-input**), an alarm can be sent via the Tetracontrol server (**tetracontrol**), or an output (**generic-output**) can be switched that is connected to another alarm input for a different system.


Producer types:
  - **generic-input** Detects an event at an input
  - **genius** Funkhandtaster Genius

Cosumer:
  - **generic-output** Switches an output.
  - **generic-printout** Only outputs a message to the log. Ideal for testing events without activating the debug log.
  - **tetracontrol** Send SDS over Tetracontrol Server.
  - **connect** Feuersoftware API for create new operation.

