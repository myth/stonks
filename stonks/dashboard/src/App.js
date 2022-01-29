import { useEffect, useRef, useState } from 'react'

import Composition from './Composition'
import Header from './Header'
import Feed from './Feed'
import Forex from './Forex'
import Indices from './Indices'
import Plot from './Plot'
import Positions from './Positions'
import { Summary } from './Summary'
import Status from './Status'
import DailyClose from './DailyClose'

import './css/App.css'

function getWebSocketURI() {
  let host = window.location.host
  const local = host.startsWith("localhost") || host.startsWith("127.0.0.1")
  host = local ? `${window.location.hostname}:8080` : host
  return `${window.location.href.startsWith("https") ? "wss" : "ws"}://${host}/ws`
}

function connectWebSocket({ onOpen, onMessage, onClose }) {
  const ws = new WebSocket(getWebSocketURI())
  ws.onopen = onOpen
  ws.onmessage = onMessage
  ws.onclose = onClose
  return ws
}

function App() {
  const ws = useRef()
  const summary = useRef()
  const header = useRef()
  const feed = useRef()
  const plot = useRef()
  const status = useRef()
  const dailyCloses = useRef()

  const [positions, setPositions] = useState([])
  const [forexData, setForexData] = useState({})
  const [composition, setComposition] = useState({})
  const [indexData, setIndexData] = useState({})

  useEffect(() => {
    if (!ws.current || !ws.current.connected) {
      ws.current = connectWebSocket({
        onOpen: handleConnected,
        onMessage: handleMessage,
        onClose: handleDisconnected
      })
    }
  }, [ws])

  function handleMessage(msg) {
    const event = JSON.parse(msg.data)
    const data = event.data

    if (event.type === "portfolio") {
      setPositions(data.positions)
      setComposition(data.composition)
      setForexData(data.exchange_rates)
      setIndexData(data.indices)
      summary.current.setState({
        marketValue: data.market_value,
        netReturn: data.net_return,
        netReturnPercent: data.net_return_percent
      })
      plot.current.addPoint(data.market_value)
    } else if (event.type === "chart") {
      plot.current.setData(data)
    } else if (event.type === "ticker") {
      feed.current.addTicker(data)
    } else if (event.type === "close") {
      dailyCloses.current.setCloses(data)
    } else if (event.type === "index") {
      setIndexData(data)
    }

    if (event.type !== "status") header.current.setState({ lastUpdate: new Date() })
    else status.current.setState(data)
  }

  function reconnect(seconds) {
    setTimeout(() => {
      console.info("Reconnecting to Stonks")
      header.current.setState({ status: "reconnecting" })
      ws.current = connectWebSocket({
        onOpen: handleConnected,
        onMessage: handleMessage,
        onClose: handleDisconnected
      })
    }, seconds * 1000)
  }

  function handleConnected() {
    header.current.setState({ status: "connected" })
    console.info("Connected to Stonks")
  }

  function handleDisconnected() {
    console.error("Disconnected from Stonks, reconnecting in 10 seconds")
    header.current.setState({ status: "disconnected" })
    reconnect(10)
  }

  return (
    <main>
      <Header ref={header} />
      <Summary ref={summary} />
      <div className="flex">
        <Positions positions={positions} />
      </div>
      <div id="chart">
        <Plot ref={plot} />
      </div>
      <div id="panels">
        <section>
          <div className="banner">Feed</div>
          <div className="banner-table">
            <Feed ref={feed} />
          </div>
        </section>
        <section>
          <div className="banner">Indices</div>
          <div className="banner-table">
            <Indices indices={indexData} />
          </div>
        </section>
        <section>
          <div className="banner">Forex</div>
          <div className="banner-table">
            <Forex forex={forexData} />
          </div>
        </section>
        <section>
          <div className="banner">Composition</div>
          <div className="banner-table">
            <Composition composition={composition} />
          </div>
        </section>
        <section>
          <div className="banner">Status</div>
          <div className="banner-table">
            <Status ref={status} />
          </div>
        </section>
      </div>
      <DailyClose ref={dailyCloses} />
    </main>
  )
}

export default App
