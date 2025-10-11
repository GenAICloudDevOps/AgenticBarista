import Head from 'next/head';
import LandingPage from '../components/LandingPage';
import ChatBot from '../components/ChatBot';

export default function Home() {
  return (
    <>
      <Head>
        <title>Coffee and AI - Where Intelligence Meets Espresso</title>
        <meta name="description" content="Experience the future of coffee ordering with our AI-powered barista assistant using LangChain and LangGraph" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      
      <main>
        <LandingPage />
        <ChatBot />
      </main>
    </>
  );
}
