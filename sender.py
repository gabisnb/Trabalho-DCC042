import UDP_secure

sender = UDP_secure.UDP_secure("localhost", 1234, 1024)
sender.send(b"Hello, World!")