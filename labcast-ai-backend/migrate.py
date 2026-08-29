import sqlite3; conn = sqlite3.connect('labcast.db'); conn.execute('ALTER TABLE document ADD COLUMN extraction_method VARCHAR DEFAULT \'Standard\''); conn.commit(); conn.close()  
