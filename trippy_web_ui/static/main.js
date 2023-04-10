'use strict'

/*
  ReconnectingWebsocket
  https://github.com/joewalnes/reconnecting-websocket
*/
!function(a,b){"function"==typeof define&&define.amd?define([],b):"undefined"!=typeof module&&module.exports?module.exports=b():a.ReconnectingWebSocket=b()}(this,function(){function a(b,c,d){function l(a,b){var c=document.createEvent("CustomEvent");return c.initCustomEvent(a,!1,!1,b),c}var e={debug:!1,automaticOpen:!0,reconnectInterval:1e3,maxReconnectInterval:3e4,reconnectDecay:1.5,timeoutInterval:2e3};d||(d={});for(var f in e)this[f]="undefined"!=typeof d[f]?d[f]:e[f];this.url=b,this.reconnectAttempts=0,this.readyState=WebSocket.CONNECTING,this.protocol=null;var h,g=this,i=!1,j=!1,k=document.createElement("div");k.addEventListener("open",function(a){g.onopen(a)}),k.addEventListener("close",function(a){g.onclose(a)}),k.addEventListener("connecting",function(a){g.onconnecting(a)}),k.addEventListener("message",function(a){g.onmessage(a)}),k.addEventListener("error",function(a){g.onerror(a)}),this.addEventListener=k.addEventListener.bind(k),this.removeEventListener=k.removeEventListener.bind(k),this.dispatchEvent=k.dispatchEvent.bind(k),this.open=function(b){h=new WebSocket(g.url,c||[]),b||k.dispatchEvent(l("connecting")),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",g.url);var d=h,e=setTimeout(function(){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",g.url),j=!0,d.close(),j=!1},g.timeoutInterval);h.onopen=function(){clearTimeout(e),(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",g.url),g.protocol=h.protocol,g.readyState=WebSocket.OPEN,g.reconnectAttempts=0;var d=l("open");d.isReconnect=b,b=!1,k.dispatchEvent(d)},h.onclose=function(c){if(clearTimeout(e),h=null,i)g.readyState=WebSocket.CLOSED,k.dispatchEvent(l("close"));else{g.readyState=WebSocket.CONNECTING;var d=l("connecting");d.code=c.code,d.reason=c.reason,d.wasClean=c.wasClean,k.dispatchEvent(d),b||j||((g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",g.url),k.dispatchEvent(l("close")));var e=g.reconnectInterval*Math.pow(g.reconnectDecay,g.reconnectAttempts);setTimeout(function(){g.reconnectAttempts++,g.open(!0)},e>g.maxReconnectInterval?g.maxReconnectInterval:e)}},h.onmessage=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",g.url,b.data);var c=l("message");c.data=b.data,k.dispatchEvent(c)},h.onerror=function(b){(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",g.url,b),k.dispatchEvent(l("error"))}},1==this.automaticOpen&&this.open(!1),this.send=function(b){if(h)return(g.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",g.url,b),h.send(b);throw"INVALID_STATE_ERR : Pausing to reconnect websocket"},this.close=function(a,b){"undefined"==typeof a&&(a=1e3),i=!0,h&&h.close(a,b)},this.refresh=function(){h&&h.close()}}return a.prototype.onopen=function(){},a.prototype.onclose=function(){},a.prototype.onconnecting=function(){},a.prototype.onmessage=function(){},a.prototype.onerror=function(){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});

const localdev = false

const $ = document.querySelector.bind(document)
const host = localdev ? '192.168.1.11' : window.location.host
const socket = new ReconnectingWebSocket(`ws://${host}/trippi`)

const ready = (callback) => {
  if (document.readyState != "loading") callback()
  else document.addEventListener("DOMContentLoaded", callback)
}

ready(() => {

  // hide overlay when connected
  socket.addEventListener('open', e => {
    // request the current state of the GU
    socket.send(JSON.stringify({ key: 'GET_STATE' }))
  })

  // show overlay when disconnected
  socket.addEventListener('close', e => {
    $('body').classList.remove('online')
  })

  // the GU only ever sends one kind of socket message,
  // in response to GET_STATE or a preset load

  socket.addEventListener('message', e => {
    const data = JSON.parse(e.data)
    $('#PRESETS').value = data.CURRENT_FILE
    setValues(data.VALUES)
    $('body').classList.add('online')
  })

  // handle button clicks
  $('#BTN_SAVE').addEventListener('click', handleSave)
  $('#BTN_SAVE_AS').addEventListener('click', handleSaveAs )

  // get the list of presets
  fetch(`http://${host}/presets`)
  .then(response => response.json())
  .then(setPresets)
})

const setPresets = presets => {
  const el = $("#PRESETS")
  // empty list
  while(el.lastChild) el.removeChild(el.lastChild)
  // add options
  presets.forEach(preset => el.appendChild(new Option(preset)))
  // listen for changes, clear old listeners first
  el.removeEventListener('change', handlePresetChange)
  el.addEventListener('change', handlePresetChange)
}

const setValues = values => {
  Object.keys(values).forEach(key => {
    const el = $(`#${key}`)
    if (key == 'DRIFT')
      el.value = JSON.stringify(values[key])
    else if (key == "TEXT")
      el.value = values[key]
    else
      el.value = $(`#${key}_VALUE`).innerHTML = values[key]
    // listen for change, clear old listeners first
    el.removeEventListener('input', handleValueChange)
    el.addEventListener('input', handleValueChange)
  })
}

const handlePresetChange = e => socket.send(JSON.stringify({key: 'LOAD', file: e.target.value}))

const handleSave = () => socket.send(JSON.stringify({ key: 'SAVE' }))

const handleSaveAs = () => {
  const file = prompt('New file name')
  if (file) {
      socket.send(JSON.stringify({ key: 'SAVE_AS', file }))
      $('#PRESETS').appendChild(new Option(file))
      $('#PRESETS').value = file
  }
}

const handleValueChange = e => {
  const { id: key, value } = e.target
  if ($(`#${key}_VALUE`)) $(`#${key}_VALUE`).innerHTML = value
  socket.send(JSON.stringify({ key, value }))
}
