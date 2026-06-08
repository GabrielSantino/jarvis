import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from "framer-motion"
import { Mic, Mic0ff, Volume2, Loader, Zap } from "lucide-react"
import { label } from 'framer-motion/client';

//URL do backend Python
const WS_URL = "ws://localhost:8000/ws"

// Estados possívevis do Jarvis
const ESTADOS = {
  idle:        { label: "Aguardando",  cor: "#4A90D9"},
  ouvindo:     { label: "Ouvindo",     cor: "#27AE60"},
  pensando:    { label: "Pensando",    cor: "#F39C12"},
  respondendo: { label: "Respondendo", cor: "#8E44AD"},
  erro:        { label: "Erro",        cor: "#E74C3C"}
}

export default function App() {
  const [estado, setEstado] = useState("idle")
  const [mensagem, setMensagens] = useState([])
  const [ferramenta, setFerramenta] = useState(null)
  const [entrada, setEntrada] = useState("")
  const [conectado, setConectado] = useState(false)
  const ws = useRef(null)
  const chatRef = useRef(null)

  // Conecta ao WebSocket quando o componente monta
  useEffect(() => {
    conectarWS()
    return () => ws.current?.close()
  }, [])

  // Rola o chat pra baixo quando novas mensagens chegam 
  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth"})
  }, [mensagens])

  function conectarWS() {
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => {
      setConectado(true)
      setEstado("idle")
    }

    ws.current.onclose = () => {
      setConectado(false)
      // Tenta reconectar após 3 segundos
      setTimeout(conectarWS, 3000)
    }

    ws.current.onmessage = (event) => {
      const dados = JSON.parse(event.data)

      if (dados.tipo === "status") {
        setFerramenta(dados.dados)
      }

      if (dados.tipo === "transcricao") {
        adicionarMEnsagem("usar", dados.dados)
      }

      if (dados.tipo === "resposta") {
        adicionarMensagem("jarvis", dados.dados)
        setEstado("idle")
        setFerramenta(null)
      }
    }
  }

  function adicionarMensagem(origem, texto) {
    setMensagens(prev => [...prev, { origem, texto, id: Date.now() }])
  }

  function enviarTexto() {
    if(!entrada.trim() || !conectado) return
    adicionarMensagem("user", entrada)
    ws.current.send(JSON.stringify({ tipo:"texto", entrada}))
    setEntrada("")
    setEstado("pensando")
  }

  function ativarVoz() {
    if(!conectado) return
    ws.current.send(JSON.stringify({ tipo: "voz"}))
    setEstado("ouvindo")
  }

  const corAtual = ESTADOS[estado]?.cor || "#4A90D9"

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0a0a0f",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "24px",
      fontFamily: "system-ui, sans-serif",
      color: "#fff"
    }}>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight:"300", letterSpacing: "8px", color: "#4a90d9" }}>
          J A R V I S
        </h1>
        <p style={{ fontSize: "12px", color: "#555", letterSpacing: "4px"}}>
          ASSISTENTE PESSOAL
        </p>
      </div>

      {/* Orbe animado - coração visual do Jarvis */}
      <div style={{ position: "relative", marginBottom: "32px" }}>

        {/* Anéis pulsantes */}
        {estado !== "idle" && [1, 2, 3].map(i => (
          <motion.div
          key={i}
          style={{
            position: "absolute",
            top: "50%", left: "50%",
            transform: "translate(-50%, -50%)",
            width: 120 + i * 40,
            height: 120 + i * 40,
            borderRadius: "50%",
            border: `1px solid ${corAtual}`,
            opacity:0
          }}
          animate={{ opacity: [0, 0.4, 0], scale: [0.8, 1.2, 1.5] }}
          transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
          />
        ))}

        {/* Orbe principal */}
        <motion.div
          animate={{
            boxShadow: [
              `0 0 30px ${corAtual}44`,
              `0 0 60px ${corAtual}88`,
              `0 0 30px ${corAtual}44`
            ],
            scale: estado === "ouvindo" ? [1, 1.05, 1] : 1
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
          style={{
            width: 120,
            height: 120,
            borderRadius: "50%",
            background: `radial-gradien(circle, ${corAtual}33, #0a0a0f)`,
            border: `2px solid ${corAtual}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            position: "relative",
            zIndex: 1
          }}
          onClick={ativarVoz}
        >
          {/* Ícone dentro do orbe*/}
          {estado === "idle" && <Mic size={36} color={corAtual} />}
          {estado === "ouvindo" && (
            <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 0.5, repeat: Infinity }}>
              <Volume2 size={36} color={corAtual} />
            </motion.div>
          )}
          {estado === "pensando" && (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear"}}>
              <Loader size={36} color={corAtual} />
            </motion.div>
          )}
          {estado === "respondendo" && <Zap size={36} color={corAtual} />}
        </motion.div>
      </div>

      {/* Status */}
      <motion.p
        key={estado}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ fontSize> "13px", color: corAtual, letterSpacing: "3px", marginBottom: "8px" }}
      >
        {ESTADOS[estado]?.label?.toUpperCase()}
      </motion.p>

      {/* Ferramenta ativa */}
      <AnimatePresence>
        {ferramenta && (
          <motion.p
            initial={{ opacity: 0}}
            animate={{ opacity: 1}}
            exit={{ opacity: 0 }}
            style={{ fontSize: "12px", color: "#888", marginBottom: "16px" }}
          >
           {ferramenta}
         </motion.p>
        )}
      </AnimatePresence>

      {/* Status de conexão */}
      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "24px" }}>
        <div style={{
          width: 8, height: 8, borderRadius: "50%",
          background: conectado ? "#27AE60" : "#E74C3C"
        }} />
        <span style={{ fontSize: "11px", color: "#555" }}>
          {conectado ? "Conectado" : "Reconectando..."}
        </span>
      </div>

      {/* Chat */}
      <div
        ref={chatRef}
        style={{
          width: "100%",
          maxWidth: "600px",
          height: "300px",
          overflowY: "auto",
          marginBottom: "16px",
          display: "flex",
          flexDirection:"column",
          gap: "12px"
        }}
      >
        <AnimatePresence>
          {mensagem.map(msg => (
            <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 20}}
            animate={{ opacity: 0, y: 0 }}
            style={{
              alignSelf: msg.origem === "user" ? "flex-end" : "flex-start",
              maxWidth: "80%",
              padding: 
            }}
          ))}
        </AnimatePresence>
      </div>
  )
}