import socket
import threading
import json
import argparse
import time
import random
import sys
from datetime import datetime

class Processo:
    def __init__(self, id_processo, config_grupo, modo_auto=False):
        self.id = id_processo
        self.config_grupo = config_grupo
        self.relogio_lamport = 0
        self.entregues = set()
        self.contador_sequencia = 0
        self.sockets = {}
        self.executando = True
        self.modo_auto = modo_auto
        
        # Configurar servidor
        self.host, self.porta = config_grupo[self.id]
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.host, self.porta))
        self.socket_servidor.listen()
        print(f"[{self.id}] Escutando em {self.host}:{self.porta}")
        
        # Iniciar thread do servidor
        threading.Thread(target=self.aceitar_conexoes, daemon=True).start()
        time.sleep(2)
        
        # Conectar aos outros processos
        for pid, (host, porta) in config_grupo.items():
            if pid != self.id:
                self.conectar_processo(pid, host, porta)
        
        # Iniciar modo apropriado
        if self.modo_auto:
            threading.Thread(target=self.enviar_automatico, daemon=True).start()
        else:
            threading.Thread(target=self.entrada_usuario, daemon=True).start()

    def conectar_processo(self, pid, host, porta):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, porta))
            self.sockets[pid] = sock
            threading.Thread(target=self.receber_mensagens, args=(sock,), daemon=True).start()
            print(f"[{self.id}] Conectado a {pid} em {host}:{porta}")
        except ConnectionRefusedError:
            print(f"[{self.id}] Conexão recusada por {pid}. Tentando novamente...")
            time.sleep(1)
            self.conectar_processo(pid, host, porta)

    def aceitar_conexoes(self):
        while self.executando:
            try:
                cliente_socket, _ = self.socket_servidor.accept()
                threading.Thread(target=self.receber_mensagens, args=(cliente_socket,), daemon=True).start()
            except:
                break

    def receber_mensagens(self, sock):
        while self.executando:
            try:
                dados = sock.recv(1024)
                if not dados:
                    break
                msg = json.loads(dados.decode())
                self.processar_mensagem(msg)
            except:
                break

    def processar_mensagem(self, msg):
        self.relogio_lamport = max(self.relogio_lamport, msg['timestamp']) + 1
        chave_msg = (msg['remetente'], msg['seq'])
        
        if chave_msg not in self.entregues:
            self.entregues.add(chave_msg)
            self.log_evento(f"Entregue: {msg['dados']} | De={msg['remetente']}", self.relogio_lamport)
            
            # Retransmitir para outros
            for pid in self.sockets:
                if pid != msg['remetente']:
                    self.enviar_mensagem(pid, msg)

    def multicast_confiavel(self, dados):
        self.relogio_lamport += 1
        self.contador_sequencia += 1
        msg = {
            'remetente': self.id,
            'seq': self.contador_sequencia,
            'dados': dados,
            'timestamp': self.relogio_lamport
        }
        self.entregues.add((self.id, self.contador_sequencia))
        self.log_evento(f"Enviado: {dados}", self.relogio_lamport)
        
        for pid in self.sockets:
            self.enviar_mensagem(pid, msg)

    def enviar_mensagem(self, pid, msg):
        try:
            msg_str = json.dumps(msg)
            self.sockets[pid].sendall(msg_str.encode())
        except:
            pass

    def enviar_automatico(self):
        time.sleep(3)
        
        mensagens = [
            "Olá a todos!",
            "Como vocês estão?",
            "Sistemas distribuídos são divertidos!",
            "Este é um teste de multicast",
            "Relógios de Lamport são úteis",
            f"Mensagem final de {self.id}"
        ]
        
        for texto in mensagens:
            intervalo = random.uniform(1, 3)
            time.sleep(intervalo)
            self.multicast_confiavel(texto)
        
        time.sleep(5)
        self.executando = False
        print(f"[{self.id}] Modo automático concluído. Pressione Ctrl+C para sair.")

    def entrada_usuario(self):
        print(f"[{self.id}] Modo manual ativo. Digite mensagens para multicast.")
        while self.executando:
            try:
                dados = input()
                if dados.lower() == 'sair':
                    self.executando = False
                    break
                if dados.strip():
                    self.multicast_confiavel(dados)
            except KeyboardInterrupt:
                self.executando = False
                break

    def log_evento(self, evento, relogio):
        hora = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{self.id}] [Lamport={relogio}] {hora} - {evento}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Processo Distribuído com Multicast Confiável')
    parser.add_argument('--id', required=True, help='ID do Processo (ex: P1)')
    parser.add_argument('--group', '--grupo', required=True, dest='grupo', help='Arquivo JSON de configuração do grupo')
    parser.add_argument('--auto', action='store_true', help='Ativar modo automático')
    args = parser.parse_args()

    with open(args.grupo, 'r') as f:
        config_grupo_raw = json.load(f)
    
    config_grupo = {}
    for pid, endereco in config_grupo_raw.items():
        host, porta = endereco.split(':')
        config_grupo[pid] = (host, int(porta))
    
    processo = Processo(args.id, config_grupo, args.auto)
    
    try:
        while processo.executando:
            time.sleep(0.5)
    except KeyboardInterrupt:
        processo.executando = False
    finally:
        print(f"[{processo.id}] Processo terminado")
        sys.exit(0)