1. Understand how ClientPasswordAuthType works with RDS Proxy
2. In scalability demo, we can showcase number of database connections and number of proxy connections to prove that proxy can take connections, but how to prove all those connections are being served. I mean, all those connections got it work done correctly without errors?
3. Why DNS doesn't take effect in the failover demo? It able to recover in just 7 seconds.
4. Will every transaction in queue will get succeed on DB failover?
5. Some situations where multiplexing may not work, Like when we change session state
	1. If your application is using session state, it is not obvious to re-use that connection
	2. For the lifetime of the application connection, it will be pinned to a specific database connection and it won't be used for multiplexed.
![Doubts - Pinning](images/Doubts%20-%20Pinning.png)
