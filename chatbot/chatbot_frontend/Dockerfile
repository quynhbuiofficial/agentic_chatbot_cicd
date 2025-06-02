FROM node:22-alpine3.20 

WORKDIR /chatbot_frontend

COPY package*.json .
RUN npm install 
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"] 