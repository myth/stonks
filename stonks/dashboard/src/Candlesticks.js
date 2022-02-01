import Chart from "react-apexcharts"
import React from "react"


export default class Candlesticks extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      options: {
        chart: {
          id: "chart",
          type: "candlestick",
          animations: { enabled: false },
          background: "black",
          toolbar: { show: false }
        },
        plotOptions: {
          candlestick: {
            colors: {
              upward: '#086814',
              downward: '#880707'
            }
          }
        },
        grid: { show: false, padding: { left: 0, right: 0 } },
        xaxis: { axisTicks: { show: false }, axisBorder: { show: false }, type: "datetime" },
        yaxis: { axisTicks: { show: false }, labels: { show: false }, axisBorder: { show: false }, },
        // stroke: { curve: "straight", width: 3 },
        theme: { mode: "dark" },
        // colors: ["#7e9724"]
      },
      series: [{ name: "Daily", data: [] }]
    }
  }

  updateLast(data) {
    const items = [...this.state.series[0].data]
    items[items.length - 1] = {
      x: data["time"] * 1000,
      y: [data["open"], data["high"], data["low"], data["close"]]
    }
    this.setState({ series: [{ name: "Hourly", data: items}]})
  }

  setData(data) {
    const items = data.map(d => {
      return {
        x: d["time"] * 1000,
        y: [d["open"], d["high"], d["low"], d["close"]]
      }
    })
    this.setState({ series: [{ name: "Hourly", data: items}]})
  }

  render() {
    return (
      <section id="chart">
        <Chart options={this.state.options} series={this.state.series} type="candlestick" width="100%" height="320" />
      </section>
    )
  }
}
