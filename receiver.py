import UDP_secure

receiver = UDP_secure.UDP_secure("localhost", 1234, 1024)
receiver.receive("localhost")