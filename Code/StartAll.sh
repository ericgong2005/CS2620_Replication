# May need to run chmod +x StartAll.sh

# Exit immediately if a command fails
set -e  

# Control C kills all models
trap "kill 0" SIGINT SIGTERM

# Check commandline arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 n HOST:PORT1 HOST:PORT2 ... HOST:PORTn"
    exit 1
fi

n=$1
shift

if [ $# -ne "$n" ]; then
    echo "Error: Expected $n HOST:PORT addresses, got $#"
    exit 1
fi

leader="$1"

# Start Leader
python GRPCServer.py "$leader" 0 &

# Start Followers
shift
for arg in "$@"; do
    python GRPCServer.py "$arg" 1 "$leader" &
done

wait

