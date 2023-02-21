import openstack
import base64
 
def b64(s):
    s = s.encode('utf-8')
    s = base64.b64encode(s)
    s = s.decode('utf-8')
    return s

conn = openstack.connect(cloud='openstack')

def listServers():
    for server in conn.compute.servers():
        if 'script' in server.tags:
            print(server.tags)
            print(server.name)
            
def delete(serverName):
 
    server = conn.compute.find_server(serverName)
    print(server.tags)   
    if 'script' in server.tags:
        conn.compute.delete_server(server)
        ip = conn.network.find_ip(serverName)
        conn.network.delete_ip(ip)
        
def create(msg):
    image = conn.compute.find_image('ubuntu server 22.04')
    flavor = conn.compute.find_flavor('f1.perfect')
    network = conn.network.find_network('mynetwork')
    keypair = conn.compute.find_keypair('MyKeyPair')

    user_data = f'''#!/bin/bash

apt-get update
apt-get install nginx -y

echo "<html><body>{msg}</body></html>" > /var/www/html/index.html
    '''

    user_data = b64(user_data)
        
    external_network = conn.network.find_network('external')
    ip = conn.network.create_ip(floating_network_id=external_network.id)
    
    server = conn.compute.create_server(
            name=ip.floating_ip_address, image_id=image.id, flavor_id=flavor.id,
            networks=[{"uuid": network.id}], key_name=keypair.name,
            user_data=user_data, security_groups=[{'name':'MySecurityGroup'}],
            tags=['script'])

    print("CREATED SERVER")
    
    conn.compute.wait_for_server(server)
    conn.compute.add_floating_ip_to_server(server, ip.floating_ip_address)
    print("SERVER IS READY", ip.floating_ip_address) 
   
wlcMsg="""
list   | list all servers
create | create a server
delete | delete a server
"""
print(wlcMsg)
 

while 1:
    command = input("> ")
    if command == "list":
        listServers()
    elif command == "create":
        msg = input("message= ")
        create(msg)
    elif command == "delete":
        name = input("server=")
        delete(name)
    else:
        print("Invalid command")

