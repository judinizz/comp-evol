#!/bin/bash
# Script para testar a API de otimização de rotas

echo "=== TESTE DA ROTA OTIMIZADA ==="
echo

curl -sS -X POST http://localhost:5000/api/optimize-route \
    -H 'Content-Type: application/json' \
    -d '{
        "startDate": "2025-12-01",
        "endDate": "2025-12-02",
        "startTime": "20:00",
        "endTime": "23:00",
        "startPoint": "Baiuca"
    }' -o /tmp/rota_test.json

echo "Processando resposta..."
echo

python3 << 'EOF'
import json

try:
    with open('/tmp/rota_test.json') as f:
        data = json.load(f)
    
    print(f"✅ Sucesso: {data.get('success')}")
    
    if not data.get('success'):
        print(f"\n❌ Erro: {data.get('error')}")
        exit(1)
    
    print()
    stats = data.get('stats', {})
    print('📊 ESTATÍSTICAS DA OTIMIZAÇÃO:')
    print(f"   • Número de paradas: {stats.get('numberOfStops')}")
    print(f"   • Distância total: {stats.get('totalDistance')}")
    print(f"   • Duração total: {stats.get('totalDuration')}")
    print(f"   • Custo (função objetivo): {stats.get('cost')}")
    print(f"   • Dias necessários: {stats.get('numberOfDays')}")
    print()
    
    bars = data.get('bars', [])
    print(f'🍺 ROTA OTIMIZADA ({len(bars)} bares):')
    print('-' * 100)
    
    for i, bar in enumerate(bars[:12], 1):
        name = bar.get('name', 'N/A')[:35]
        arrival = bar.get('arrivalTime', 'N/A')
        departure = bar.get('departureTime', 'N/A')
        lat = bar.get('lat', 0)
        lng = bar.get('lng', 0)
        travel = bar.get('travelTimeToNext', 0)
        print(f"{i:2d}. {name:35s} | {arrival} → {departure} | Próx: {travel:4.0f}min | ({lat:.5f}, {lng:.5f})")
    
    if len(bars) > 12:
        print(f"    ... e mais {len(bars)-12} bares")
    
    print()
    print("✅ Teste concluído com sucesso!")
    
except FileNotFoundError:
    print("❌ Erro: Arquivo de resposta não encontrado")
    exit(1)
except json.JSONDecodeError:
    print("❌ Erro: Resposta JSON inválida")
    exit(1)
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    exit(1)
EOF
