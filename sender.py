import UDP_secure

sender = UDP_secure.UDP_secure("localhost", 1235, 1024)
sender.send("localhost", 1234, b"Hello, World!")
sender.waitAck()