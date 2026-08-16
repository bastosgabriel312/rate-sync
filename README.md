# RateSync

**RateSync** é um sistema desenvolvido em Python utilizando FastAPI, que reúne e exibe avaliações de filmes e séries de várias plataformas populares, como IMDb, Rotten Tomatoes, Metacritic, entre outras, através de APIs oficiais. O objetivo do RateSync é permitir que os usuários consultem, de forma rápida e simples, as avaliações mais relevantes de diversas fontes em um único lugar.

## Funcionalidades

- **Pesquisa Personalizada**: Os usuários podem buscar por filmes e séries utilizando uma caixa de pesquisa, retornando resultados baseados em títulos parciais ou completos.
- **Consolidação de Dados**: Reúne e exibe as notas médias e o número de avaliações de diferentes plataformas em uma tabela consolidada.
- **Atualização em Tempo Real**: Os dados são consultados e reunidos no momento da pesquisa, garantindo que as informações estejam sempre atualizadas.
- **Interface Minimalista**: Foco em uma experiência de usuário limpa e direta, com fácil navegação e acesso rápido às informações.

## Tecnologias Utilizadas

- **Linguagem**: Python
- **Framework**: FastAPI
- **Gerenciador de Pacotes**: pip
- **Servidor Web**: Uvicorn

## Créditos

- **LetterboxdPy**: Biblioteca para integração com a API do Letterboxd. Disponível em [GitHub](https://github.com/nmcassa/letterboxdpy). Agradecimentos a [nmcassa](https://github.com/nmcassa) por manter e atualizar este projeto.
- **OMDb API**: API de dados sobre filmes e séries. Agradecimentos a [OMDb API](https://www.omdbapi.com/) por fornecer acesso a informações detalhadas sobre filmes e programas de TV.
- **Cinemeta**: Addon da [Stremio](https://www.stremio.com/) que fornece catálogo e metadados de filmes sem necessidade de API key.

