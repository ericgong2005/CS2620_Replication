pids=$(ps aux | grep '[G]RPCServer.py' | awk '{print $2}')

if [ -z "$pids" ]; then
  echo "Clean"
else
  echo "Cleaning"
  for pid in $pids; do
    kill -9 "$pid"
  done
fi