# Engineering Notebook

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
