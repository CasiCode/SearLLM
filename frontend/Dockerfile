FROM node:latest

WORKDIR /workspace

COPY package*.json ./

RUN npm install

COPY . .

CMD [ "node", "server.js" ]