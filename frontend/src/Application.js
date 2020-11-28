//import { List, ListItem } from 'rmwc';
import  {Component} from 'react'
//import { Button } from '@rmwc/button';
import {List, SimpleListItem, Typography} from 'rmwc'
import {Card,CardPrimaryAction, CardActions, CardActionButtons,CardActionButton} from '@rmwc/card'
import {Grid, GridCell, GridRow} from '@rmwc/grid'
import './Application.css'
import '@rmwc/grid'
//css imports

import '@rmwc/list/styles';
import '@rmwc/icon/icon.css';
import '@rmwc/card/styles';
import '@rmwc/grid/styles';
URL = 'ws://185.245.96.117:8765'
class BlockChain extends Component{
    constructor(){
        super()
        this.state = {
            name: 'Bob',
            messages: [],
            chain: [],
            renderCollection: []
        }
    }
    
    ws = new WebSocket(URL)

    componentDidMount() {
        this.ws.onopen = () => {
        console.log('connected')
        console.log(this.ws.send(JSON.stringify({type:'getChain'})))
        }

        this.ws.onmessage = evt => {
        const message = JSON.parse(evt.data)
        switch (message.type) {
            case 'chainData':
                var chain = JSON.parse(message.data)
                for (var block in Object.entries(chain)){
                    this.state.chain.push(chain[block])
                    this.state.renderCollection.push(<SimpleListItem
                        text="Cookies"
                        secondaryText="Chocolate chip"
                        metaIcon="info"
                        key = {chain[block].index}
                      />)
                }
                this.state.renderCollection.splice(0,this.state.renderCollection.length -2)
                break
            default:
                break

        }
        this.addMessage(message)
        }

        this.ws.onclose = () => {
        console.log('disconnected')
        this.setState({
            ws: new WebSocket(URL),
        })
        }
    }

    addMessage = message =>
        this.setState(state => ({ messages: [message, ...state.messages] }))

    submitMessage = messageString => {
        const message = { name: this.state.name, message: messageString }
        this.ws.send(JSON.stringify(message))
        this.addMessage(message)
    }

    render(){
        return(
            <div id="blockListContainer">
            <Grid id='grid'>
                <GridRow>
                    <GridCell span ={3}>
                        <Card id="bl1" className='blockList tall'>
                            <List twoLine>
                                {this.state.renderCollection}
                            </List>
                        </Card>
                    </GridCell>
                    <GridCell span ={3}>
                        <Card id="bl1" className='blockList tall'>
                            <List twoLine>
                                {this.state.renderCollection}
                            </List>
                        </Card>
                    </GridCell>
                    <GridCell span ={6}>
                        <Card id="bl2" className='blocklist small'>
                            <List twoLine>
                                {this.state.renderCollection}
                            </List>
                        </Card>
                        <Card id="bl3" className='blocklist small'>
                            <List twoLine>
                                {this.state.renderCollection}
                            </List>
                        </Card>
                    </GridCell>
                </GridRow>
            </Grid>
            </div>
        )
    }
}
export default BlockChain;
