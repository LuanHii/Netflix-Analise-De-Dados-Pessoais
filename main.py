import matplotlib.pyplot as plt
import pandas as pd

serie_desejada = input("Digite o nome da série desejada: ")
perfil_desejado = input("Digite o nome do perfil desejado: ")
arquivo_csv = 'ViewingActivity.csv'
dados_netflix = pd.read_csv(arquivo_csv)

colunas_indesejadas = ['Attributes', 'Supplemental Video Type', 'Device Type', 'Bookmark', 'Latest Bookmark', 'Country']
dados_netflix = dados_netflix.drop(colunas_indesejadas, axis=1)

dados_netflix['Start Time'] = pd.to_datetime(dados_netflix['Start Time'], utc=True)
dados_netflix['Ano'] = dados_netflix['Start Time'].dt.year
dados_netflix['Mês'] = dados_netflix['Start Time'].dt.month
dados_netflix['Dia'] = dados_netflix['Start Time'].dt.day
dados_netflix['Hora'] = dados_netflix['Start Time'].dt.hour
dados_netflix['Minuto'] = dados_netflix['Start Time'].dt.minute
dados_netflix['Segundo'] = dados_netflix['Start Time'].dt.second

dados_netflix = dados_netflix.set_index('Start Time')
dados_netflix.index = dados_netflix.index.tz_convert('America/Sao_Paulo')
dados_netflix = dados_netflix.reset_index()

dados_netflix['Duração'] = pd.to_timedelta(dados_netflix['Duration'])

perfil_especifico = dados_netflix[dados_netflix['Profile Name'] == perfil_desejado]

perfil_especifico_serie = perfil_especifico[perfil_especifico['Title'].str.contains(serie_desejada, case=False)]
perfil_especifico_serie = perfil_especifico_serie[(perfil_especifico_serie['Duração'] > '0 days 00:02:00')]


perfil_especifico_serie = perfil_especifico_serie.drop_duplicates(subset=['Title', 'Start Time'])

perfil_especifico_serie['dia_da_semana'] = perfil_especifico_serie['Start Time'].dt.weekday
perfil_especifico_serie['hora'] = perfil_especifico_serie['Duração'].dt.total_seconds() / 3600  # Converte a duração para horas

print(perfil_especifico_serie['Duração'].sum())
print(perfil_especifico_serie.head(1))

perfil_especifico_serie['dia_da_semana'] = pd.Categorical(perfil_especifico_serie['dia_da_semana'], categories=[0, 1, 2, 3, 4, 5, 6], ordered=True)

perfil_dia_soma = perfil_especifico_serie.groupby('dia_da_semana', observed=False)['hora'].sum()
perfil_dia_soma = perfil_dia_soma.sort_index()

mapeamento_dias = {
    0: 'Segunda-feira',
    1: 'Terça-feira',
    2: 'Quarta-feira',
    3: 'Quinta-feira',
    4: 'Sexta-feira',
    5: 'Sábado',
    6: 'Domingo'
}

dias_semana = [mapeamento_dias[day] for day in perfil_dia_soma.index]


perfil_especifico_serie.to_csv('perfil_especifico_serie.csv', index=False)

plt.figure(figsize=(20, 10))
perfil_dia_soma.plot(kind='bar', title=f"Horas de {serie_desejada} assistidas por dia da semana", fontsize=24)
plt.ylabel('Horas assistidas no dia', fontsize=23)
plt.xlabel('Dia', fontsize=23)


plt.yticks([int(count) for count in plt.yticks()[0]])

plt.xticks(range(len(dias_semana)), dias_semana, rotation=45)
plt.subplots_adjust(bottom=0.5)


total_horas = perfil_especifico_serie['hora'].sum()
plt.text(0.5, -0.8, f'Total de Horas Assistidas em {serie_desejada}: {total_horas:.2f} horas', ha='center', va='center', transform=plt.gca().transAxes, fontsize=20)

plt.show()
