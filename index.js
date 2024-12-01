
const express = require('express');
const app = express()
const fs = require('node:fs')
const util = require('util');
const readFile = util.promisify(fs.readFile);
const axios = require("axios");

const cors = require('cors');
app.use(cors());

app.use(express.json())

//PARAMETERS
const PORT = 6465
const userinfo = './/userStocks.txt'
const avkey = "RE2H8GRCGHMPVOMB"
const url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=IBM&apikey=${avkey}`;


const jsstr = fs.readFileSync(userinfo);
const stocks = JSON.parse(jsstr);

app.listen(
    PORT,
    () => console.log(`Alive on http://localhost:${PORT}`)
)

//returns list of stocks on the watchlist
app.get('/stocks', async (req, res) => {
    res.status(200).send(
        JSON.stringify(stocks)
    )
})

//get the price update for a stock on the watchlist
app.get('/stocks/:symbol', async (req,res) => {
    const  stock_symbol  = req.params.symbol
    let matches = 0
    let idx = -1
    for(let i = 0; i < stocks.length; i++){
        if (stocks[i].symbol === stock_symbol){
            matches += 1;
            idx = i
        }
    }
    if (matches < 1){
        res.status(400).send({
            "status":400,
            "error":`Stock with symbol ${stock_symbol} not found in your collection.`
        })
        
    }else{
        const  stock_url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${stock_symbol}&apikey=${avkey}`
        const response = await axios.get(stock_url);
        const data = response.data;
        if (data["Global Quote"].length === 0){
            res.status(400).send({
                "status":400,
                "error":`Stock with symbol ${stock_symbol} not found.`
            })
        
        }else{    
            const new_price = data["Global Quote"]["05. price"];
            const diff = new_price - stocks[idx].orig_price;
            stocks[idx].curr_price = new_price;
            res.status(200).send({
                "status":200,
                "message": "Success",
                "stocks": [
                    {"id": idx,
                    "symbol": stocks[idx].symbol,
                    "original_price": stocks[idx].orig_price,
                    "new_price": stocks[idx].curr_price,
                    "change": diff}
                ]

            })
        }
    }   
})

//Add a new stock to the watchlist by symbol (e.g. IBM)
app.post('/stocks/:symbol' ,async (req, res) => {
    const  stock_symbol  = req.params.symbol
    const  stock_url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${stock_symbol}&apikey=${avkey}`
    const response = await axios.get(stock_url);
    const data = response.data;
    if (data["Global Quote"].length === 0){
        res.status(400).send({
            "status":400,
            "error":`Stock with symbol ${stock_symbol} not found.`,
            "stocks": []
        })
    }else{

        const stock = {
            id: stocks.length + 1,
            symbol: stock_symbol,
            orig_price: data["Global Quote"]["05. price"],
            curr_price: data["Global Quote"]["05. price"]
        }
        console.log(`Added stock: ${stock}`)
        stocks.push(stock)
        writeStocks(stocks)
        res.send(stock)
    }
})

//clear the watchlist
app.post('/clearall', (req,res) => {
    stocks.length = 0;
    writeStocks(stocks)
    res.send('Successfully cleared stock watchlist.');
}) 

//delete a stock on the watchlist
app.delete('/stocks/:symbol',(req,res) =>{
    const stock_symbol = req.params.symbol;
    for(let i = 0; i < stocks.length; i++){
        if (stocks[i].symbol = stock_symbol){
            stocks.splice(i,1)
            res.send(`Deleted ${stock_symbol}`);
        }
    }
    writeStocks(stocks)
})


//get a daily summary of stocks on the watchlist
app.get('/summary',async (req,res) => {
    let sinf = []
    for(let i = 0; i < stocks.length; i++){
        const stock_symbol = stocks[i].symbol
        const  stock_url = `https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${stock_symbol}&apikey=${avkey}`
        const response = await axios.get(stock_url);
        const data = response.data;
        const coinSum = {
            "symbol" : stocks[i].symbol,
            "low" : data["Global Quote"]["04. low"],
            "high" : data["Global Quote"]["03. high"],
            "volume" : data["Global Quote"]["06. volume"],
            "change" : data["Global Quote"]["09. change"],
            "change percent" : data["Global Quote"]["10. change percent"]
        }
        sinf.push(coinSum)
    }
    res.status(200).send({
        "status":200,
        "message":`Success`,
        "stocks": sinf
    })

}) 

function writeStocks(stocks){
    const content = JSON.stringify(stocks)
    fs.writeFile(userinfo, content, err => {
        if (err) {
          console.error(err);
        } else {
          // file written successfully
          console.log(`Wrote user's stocks to file`);
        }
      });
}