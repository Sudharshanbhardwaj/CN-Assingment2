import os, sys
import re, time
import subprocess
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI, info
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
import matplotlib.pyplot as plt

def plot_tput_graph(file_read,save_path=None):
    # Read file at the file_read a text file
    with open(file_read, 'r') as file:
        data = file.read()
        
    # Extract the tcp throughput values and time intervals using regular expressions
    # Tput = throughput
    tput_values = re.findall(r'(\d*\.?\d*) GBytes/sec', data)
    time_values = re.findall(r'-(\d+\.\d+) ', data)
    
    # Convert the values to float type
    tput_values = [0] + [float(i) for i in tput_values]
    time_values = [0] + [float(i) for i in time_values]
    
    print(len(tput_values))
    print(len(time_values))
    # Plot the graph of throughput vs time
    plt.figure()
    plt.plot(time_values, tput_values, marker='o')
    plt.title('Time vs Throughput')
    plt.ylabel('TCP Throughput (Gbits/sec)')
    plt.xlabel('Time (sec)')
    plt.grid(True)
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
    else:
        plt.show()
   

class MyTopo(Topo):
    def __init__(self, link_loss=0):
        Topo.__init__(self)

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2, loss = link_loss)

def start_server(host, server_file, congestion="reno"):
    server_cmd = f'iperf -s -t 5 -i 0.1 -p 5001 -f G -Z {congestion} > {server_file}'
    print(server_cmd)
    return host.popen(server_cmd, shell=True)

def start_client(host, client_file, congestion="reno", hostip=""):
    client_cmd = f'iperf -c {hostip} -t 5 -i 0.1 -p 5001 -f G -Z {congestion} > {client_file}'
    print(client_cmd)
    client_process = host.popen(client_cmd, shell=True)
    return client_process

            
def main():
    if len(sys.argv) < 7:
        print("Usage: sudo python code.py --config <value> --congestion <value> --loss <value>")
        sys.exit(1)

    # Parse the command-line arguments
    config_index = sys.argv.index("--config")
    congestion_index = sys.argv.index("--congestion")
    loss_index = sys.argv.index("--loss")

    config = sys.argv[config_index + 1]
    congestion = sys.argv[congestion_index + 1]
    loss = sys.argv[loss_index + 1]

    if (config == None):
        print("Please provide config parameter like --config b or --config c **for part d of the question use config b with loss [1/3]**")
        return 0
    if (config == 'b' or config == 'c'):
        if (congestion == None):
            print("Please provide congestion parameter like --congestion reno/cubic/bbr/vegas")
            return 0
        else:
            #check  if the congestion parameter is valid
            if congestion not in ["reno","bbr","vegas","cubic"]:
                print("Please provide congestion parameter like --congestion reno/cubic/bbr/vegas")
                return 0
   
    
    # Code to print the arguments
    print(config, congestion, loss)

    topo = MyTopo(loss)
    net = Mininet(topo)
    net.start()
    
    # For Part d also use --Config b with --loss [1/3]      
    if config == 'b':
        for host in ['h1','h4']:
                    os.makedirs(f"./b/text/{host}",exist_ok=True)
          
        congestions = ["reno","bbr","vegas","cubic"]
        print("Part b: Running h4 as the server and h1 as the client")
                
        for congestion in congestions:
            print(f"************** {congestion} **************")
	    # Starting h4 server
            h4_server_file = f"./b/text/h4/b_h4_server_{congestion}loss{loss}.txt"
            server_process = start_server(net['h4'], h4_server_file,congestion)
            time.sleep(1)
            # Starting client h1
            h1_client_file = f"./b/text/h1/b_h1_client_{congestion}loss{loss}.txt"
            client_process = start_client(net['h1'], h1_client_file,congestion,"10.0.0.4")
            server_process.wait()
            client_process.wait()
            plot_tput_graph(h1_client_file,"./b/plots/h1/h1_client_"+congestion+"loss"+loss+".png")
            plot_tput_graph(h4_server_file,"./b/plots/h4/h4_server_"+congestion+"loss"+loss+".png")

    if config == 'c':
                for host in ['h1', 'h2', 'h3','h4']:
                    os.makedirs(f"./c/text/{host}", exist_ok=True)
                congestions = ["reno","bbr","vegas","cubic"]
                print("Part c: Running h4 as the server and h1,h2,h3 are the clients")
                for congestion in congestions:
                    print(f"************** {congestion} ***************")
		    # Starting h4 server
                    h4_server_file = f"./c/text/h4/c_h4_server_{congestion}.txt"
                    server_process = start_server(net['h4'], h4_server_file,congestion)
                    time.sleep(1)
		    # Starting clients h1 h2 h3
                    h1_client_file = f"./c/text/h1/c_h1_client_{congestion}.txt"
                    h1_client_process = start_client(net['h1'], h1_client_file,congestion,"10.0.0.4")
                    h2_client_file = f"./c/text/h2/c_h2_client_{congestion}.txt"
                    h2_client_process = start_client(net['h2'], h2_client_file,congestion,"10.0.0.4")
                    h3_client_file = f"./c/text/h3/c_h3_client_{congestion}.txt"
                    h3_client_process = start_client(net['h3'], h3_client_file,congestion,"10.0.0.4")
                    server_process.wait()
                    h1_client_process.wait()
                    h2_client_process.wait()
                    h3_client_process.wait()
                    plot_tput_graph(h1_client_file,"./c/plots/h1/h1_client_"+congestion+".png")
                    plot_tput_graph(h2_client_file,"./c/plots/h2/h2_client_"+congestion+".png")
                    plot_tput_graph(h3_client_file,"./c/plots/h3/h3_client_"+congestion+".png")
                    plot_tput_graph(h4_server_file,"./c/plots/h4/h4_server_"+congestion+".png")

            
    print("Dumping host connections")
    dumpNodeConnections(net.hosts)
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    main()
    info('Done.\n')
    print('Use sudo mn -c command to clear any reciding connections.\n')
