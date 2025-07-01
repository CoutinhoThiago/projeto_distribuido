# Reliable Multicast with Lamport Clocks

## Descrição
Implementação de um sistema distribuído com multicast confiável usando o algoritmo de flooding e relógios lógicos de Lamport. Suporta modo manual e automático.

## Pré-requisitos
- Python [3.13.5](https://www.python.org/downloads/release/python-3135/)

## Como Executar no VS Code

### 1. Organização dos Arquivos
1. Os arquivos `process.py` e `config.json` devem estar na mesma pasta

2. Abra a pasta no VS Code:
    - File > Open Folder (selecione a pasta com os arquivos)

### 2. Abara os terminais
1. Abra 3 terminais:
    - Terminal > New Terminal


### 3. Modo Automático (demonstração)
Execute em 3 terminais separados:
```bash
# Terminal 1:
python process.py --id P1 --group config.json --auto

# Terminal 2:
python process.py --id P2 --group config.json --auto

# Terminal 3:
python process.py --id P3 --group config.json --auto
```

### 4. Modo Manual (interativo)
Execute em 3 terminais separados (sem --auto):
```bash
# Terminal 1:
python process.py --id P1 --group config.json

# Terminal 2:
python process.py --id P2 --group config.json

# Terminal 3:
python process.py --id P3 --group config.json
```

## Estrutura de Arquivos
```bash
projeto_distribuido/
├── process.py          # Código principal
├── config.json         # Configuração dos processos
└── README.md           # Documentação
```

## Saída Esperada (Modo Automático)

```bash
[P1] Escutando em localhost:5001
[P1] Conectado a P2 em localhost:5002
[P1] Conectado a P3 em localhost:5003
[P1] [Lamport=1] 10:00:00.123 - Enviado: Olá a todos!
[P2] [Lamport=2] 10:00:00.234 - Entregue: Olá a todos! | De=P1
[P3] [Lamport=2] 10:00:00.245 - Entregue: Olá a todos! | De=P1
[P2] [Lamport=3] 10:00:02.450 - Enviado: Como vocês estão?
[P1] [Lamport=4] 10:00:02.465 - Entregue: Como vocês estão? | De=P2
[P3] [Lamport=3] 10:00:02.480 - Entregue: Como vocês estão? | De=P2
[P3] [Lamport=4] 10:00:05.789 - Enviado: Mensagem final de P3
[P1] [Lamport=5] 10:00:05.800 - Entregue: Mensagem final de P3 | De=P3
[P2] [Lamport=5] 10:00:05.810 - Entregue: Mensagem final de P3 | De=P3
[P3] Modo automático concluído. Pressione Ctrl+C para sair.
```