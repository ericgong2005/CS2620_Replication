# Documentation

## Table of Contents
 - Usage
 - Overview
 - Leader Election
 - Server Startup and Joining New Followers
 - Testing

## Usage
To start a client, run python GRPCClient.py (Leader Address), followed optionally by a number *n*, and *n* addresses indicating follower processes. (This second portion is optional, the leader will communicate followers with the client naturally)

To start a server leader, run python GRPCServer.py (Leader Address), followed optionally by a number *n*, and *n* addresses indicating follower processes. Follower processes MUST have a lexicographically higher address, otherwise, the proccess will assume it is a follower and attempt to connect to the address that is lower (which it believes to be the leader)

To start a server follower, run python GRPCServer.py (Follower Address), followed by a number *n*, and *n* addresses indicating the leader process and follower processes. The leader address must be specified, and followers can be specified optionally.

To start an entire replication server, run StartAll.sh followed by a number *n*, followed by *n* addresses. The first will be the leader (thus it should have the lowest lexicographic address), and the other will be the followers. Note that StartAll.sh can only start a replication server on one device! All addresses must have the same host.

To start followers only, run StartFollowers.sh followed by a number *n*, followed by *n* addresses. The first will be the leader (thus it should have the lowest lexicographic address), and the other will be the followers. The script will not attempt to start a process at the leader address. Note that StartFollowers.sh can only start followers on one device! All follower addresses must have the same host, although the leader can be a different host.

## Overview
To ensure we design a system where the separate databases are as close to consistent as possible, we choose to designate a single leader and designate all other processes to be followers. The leader process would be the only one entitled to writing to the database. When changes are made, the leader process pushes changes out to the follower processes by serializing the database. This process also allows the leader to detect if a particular follower has failed, and become unresponsive. The leader updates a list of active processes during this process, which is also pushed out to the followers, so that all followers know the list of followers that currently exist.

## Leader Election
The leader is always the process with the lexicographically lowest address, when this address is expressed as a string. Each follower periodically sends the leader a heartbeat, on a duration interval specified within Constants.py. If this fails, then the followers determine the leader to be dead. The followers then consult their list of active processes and the next lowest address becomes the leader. The followers confirm the new leader by establishing a connection to the new leader, and the leader establishes its position by pushing out the new list of followers.

The client also maintains a list of active processes, so that it too can connect to the new leader, should the old leader fail.

## Server Startup and Joining New Followers
Starting up the server via GRPCServer.py will allow one to specify the address of the current process, but also additional addresses coresponding to the other processes in the replicated server. In particular, all follower processes must be at least given the address of the leader. 

When the leader is started up, it will find the most recently edited database, and delete all other copies of the database, which may be a remanent from previous runs. It is valid to use the most recent database, given that all databases except the leader's database is updated atomically. Thus, either the most recently edited database is the leaders database, or it is a followers database that necessarily matches the leader's database.

When followers start up, they will request a copy of the leader's database. This also gives the leader a chance to verify that no follower with the same address as another follower is attempting to connect. The leader can return an error to the follower, forcing the follower to exit, should such a case occur. This ensures that the address serves as a UUID by which leader elections can occur.

Note that it is possible to start up multiple leaders, if you start a follower without providing a leader to connect to (If no leader is provided, the follower assumes it is the leader, and thus, this coudl create multiple leaders). We conceed this is an issue, but also note that start-up is outside the specification of the assignment. In addition partition is also outside the specification of the assignment. 

However, this flexible process, although it risks partitions, allows for an arbitrary number of followers to connect, at any time during the servers execution. This means that we can scale up the replication to defend against any arbitrary number of fail/stop errors (for instance, to be 5-fault tolerant, we need only to connect 5 followers to the leader). This also allows for recovery after faults, in that we can replenish the number of followers after faults.

## Testing
We begin with simple unit testing, which can executed via tests.sh. This script confirms the functionality of the leader process' ability to update the database.

We also provide a framework for advanced integration testing and role-playing based testing. In particular, the TerminalClient can be started with the same commandline argument options as the GRPCClient, and is a terminal version of the client that can be used to test the fault tolerance of the replication server. We also directly test the entire framework by running the server normally, and experimenting with fault recovery when processes are killed with kill -9 PID, where we can choose to kill the leader or the followers.