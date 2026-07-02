import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from "framer-motion"
import { Mic, Volume2, Loader, Zap } from "lucide-react"

const WS_URL = "ws://localhost:8000/ws"

const ESTADOS = {
  idle:        { label: "Aguardando",  cor: "#4A90D9" },
  ouvindo:     { label: "Ouvindo",     cor: "#27AE60" },
  pensando:    { label: "Pensando",    cor: "#F39C12" },
  respondendo: { label: "Respondendo", cor: "#8E44AD" },
  erro:        { label: "Erro",        cor: "#E74C3C" },
}

export default function App() {
  const [estado, setEstado] = useState("idle")
  const [mensagens, setMensagens] = useState([])
  const [ferramenta, setFerramenta] = useState(null)
  const [entrada, setEntrada] = useState("")
  const [conectado, setConectado] = useState(false)
  const ws = useRef(null)
  const chatRef = useRef(null)
  const conectarWSRef = useRef(null)

  const conectarWS = useCallback(() => {
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => {
      setConectado(true)
      setEstado("idle")
    }

    ws.current.onclose = () => {
      setConectado(false)
      setTimeout(() => conectarWSRef.current?.(), 3000)
    }

    ws.current.onmessage = (event) => {
      const dados = JSON.parse(event.data)

      if (dados.tipo === "status") {
        setEstado(dados.dados === "conectado" ? "idle" : dados.dados)
        setFerramenta(null)
      }
      if (dados.tipo === "ferramenta") {
        setFerramenta(dados.dados)
      }
      if (dados.tipo === "transcricao") {
        adicionarMensagem("user", dados.dados)
      }
      if (dados.tipo === "resposta") {
        adicionarMensagem("jarvis", dados.dados)
        setEstado("idle")
        setFerramenta(null)
      }
    }
  }, [])

  useEffect(() => {
    conectarWSRef.current = conectarWS
  }, [conectarWS])

  useEffect(() => {
    conectarWS()
    return () => ws.current?.close()
  }, [conectarWS])

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: "smooth" })
  }, [mensagens])

  function adicionarMensagem(origem, texto) {
    setMensagens(prev => [...prev, { origem, texto, id: Date.now() }])
  }

  function enviarTexto() {
    if (!entrada.trim() || !conectado) return
    adicionarMensagem("user", entrada)
    ws.current.send(JSON.stringify({ tipo: "texto", entrada }))
    setEntrada("")
    setEstado("pensando")
  }

  function ativarVoz() {
    if (!conectado) return
    ws.current.send(JSON.stringify({ tipo: "voz" }))
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

      <div style={{ textAlign: "center", marginBottom: "32px" }}>
        <h1 style={{ fontSize: "28px", fontWeight: "300", letterSpacing: "8px", color: "#4A90D9" }}>
          J A R V I S
        </h1>
        <p style={{ fontSize: "12px", color: "#555", letterSpacing: "4px" }}>
          ASSISTENTE PESSOAL
        </p>
      </div>

      <div style={{ position: "relative", marginBottom: "32px" }}>
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
              opacity: 0
            }}
            animate={{ opacity: [0, 0.4, 0], scale: [0.8, 1.2, 1.5] }}
            transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
          />
        ))}

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
            background: `radial-gradient(circle, ${corAtual}33, #0a0a0f)`,
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
          {estado === "idle" && <Mic size={36} color={corAtual} />}
          {estado === "ouvindo" && (
            <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 0.5, repeat: Infinity }}>
              <Volume2 size={36} color={corAtual} />
            </motion.div>
          )}
          {estado === "pensando" && (
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}>
              <Loader size={36} color={corAtual} />
            </motion.div>
          )}
          {estado === "respondendo" && <Zap size={36} color={corAtual} />}
        </motion.div>
      </div>

      <motion.p
        key={estado}
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ fontSize: "13px", color: corAtual, letterSpacing: "3px", marginBottom: "8px" }}
      >
        {ESTADOS[estado]?.label?.toUpperCase()}
      </motion.p>

      <AnimatePresence>
        {ferramenta && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ fontSize: "12px", color: "#888", marginBottom: "16px" }}
          >
            {ferramenta}
          </motion.p>
        )}
      </AnimatePresence>

      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "24px" }}>
        <div style={{
          width: 8, height: 8, borderRadius: "50%",
          background: conectado ? "#27AE60" : "#E74C3C"
        }} />
        <span style={{ fontSize: "11px", color: "#555" }}>
          {conectado ? "Conectado" : "Reconectando..."}
        </span>
      </div>

      <div
        ref={chatRef}
        style={{
          width: "100%",
          maxWidth: "600px",
          height: "300px",
          overflowY: "auto",
          marginBottom: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "12px"
        }}
      >
        <AnimatePresence>
          {mensagens.map(msg => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                alignSelf: msg.origem === "user" ? "flex-end" : "flex-start",
                maxWidth: "80%",
                padding: "12px 16px",
                borderRadius: msg.origem === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                background: msg.origem === "user" ? "#1a2a4a" : "#1a1a2e",
                border: `1px solid ${msg.origem === "user" ? "#4A90D9" : "#8E44AD"}22`,
                fontSize: "14px",
                lineHeight: "1.6",
                color: "#ddd"
              }}
            >
              <span style={{ fontSize: "10px", color: "#555", display: "block", marginBottom: "4px" }}>
                {msg.origem === "user" ? "Você" : "Jarvis"}
              </span>
              {msg.texto}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div style={{ display: "flex", gap: "8px", width: "100%", maxWidth: "600px" }}>
        <input
          value={entrada}
          onChange={e => setEntrada(e.target.value)}
          onKeyDown={e => e.key === "Enter" && enviarTexto()}
          placeholder="Digite ou clique no orbe para falar..."
          style={{
            flex: 1,
            padding: "12px 16px",
            borderRadius: "12px",
            border: "1px solid #333",
            background: "#111",
            color: "#fff",
            fontSize: "14px",
            outline: "none"
          }}
        />
        <button
          onClick={enviarTexto}
          style={{
            padding: "12px 20px",
            borderRadius: "12px",
            border: "none",
            background: "#4A90D9",
            color: "#fff",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          Enviar
        </button>
      </div>
    </div>
  )
}