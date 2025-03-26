# Engineering Notebook

## Bug Fixes:
- Initially, a server process, upon startup, believes it is the leader if its address:portname is the lowest in the list of server processes. This gave us a problem because if a machine with a lower IP address than the leader starts a server process when specifying a leader to connect to, it still thinks it's the leader because its IP address is lower than the leader's. We fixed this by specifying that in order to start as a leader, a server process must not specify a different leader.
- We also ran into an issue where the server would deadlock when the original leader was killed and it elected itself as the new leader. This happened because we were making a gRPC call within a gRPC call.

## Heartbeat Ideas:
 - Currently, everyone is sending a hearbeat request to the leader, via the loop in main
 - This allows the others to discover when the leader is dead
 - However, for the leader to know who is sending heartbeat requests, we need to include address in the heartbeat request
 - Another way would be for the leader to heartbeat all the followers, this would allow the leader to boot up new processes
 - Then, the followers would need to track the most recent communication from the leader, which might be problematic if the leader is slowed down (ie: timing based tracking)
 - It might be better to keep the followers sending the heartbeats periodically, and the leader can track who is alive based on recieved heartbeats. the leader can maintain a list of "most recent communications", and declare death on followers who havent heartbeated for a certain duration.

## Initial Ideas:
 - Use gRPC for simplicity of design, and ease of expansion and adding new commands
 - Have a single leader process handle all client communications. This removes the complications of passing to the leader
 - Have the leader, upon any database writes, inform the follower processes
 - The leader and followers all know each other given that the host:port are passed at start time
 - If there are less than two active followers, the leader will make more followers (probably through the spawn multiprocessing call)
 - The leader serializes its database for the follower
 - If the leader dies, the follower with the lower alphanumeric host:port becomes the leader. This works as  UUID since there is at most one process per host:port. This means that we can't be using 127.0.0.1 or other localhost hostnames
 - It will be easier just to start the leader process, and have it boot up its followers normally
 - The client will need to be informed of the leader and the followers, so that it can know who the next leader is
 - The followers and leaders should kill themselves upon any errors being detected
 - New followers will always use the next largest availible port number.
 - Will probably want to include list of all active processes during every communication
