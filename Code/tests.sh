# May need to run chmod +x tests.sh

# Make test director
mkdir Databases/Test

# Exit immediately if a command fails
set -e  

# Clear the databases by deleting them
rm -f Databases/Test/messages.db
rm -f Databases/Test/passwords.db
touch Databases/Test/messages.db
touch Databases/Test/passwords.db

# Start the GRPC server in the background
python GRPCServer.py 127.0.0.1:2620 0&
SERVER_PID=$!
sleep 2

# Run pytest on tests.py
pytest tests.py

# After tests finish, stop the GRPC server
kill $SERVER_PID

# Clear the databases by deleting them
rm -f Databases/Test/messages.db
rm -f Databases/Test/passwords.db
touch Databases/Test/messages.db
touch Databases/Test/passwords.db