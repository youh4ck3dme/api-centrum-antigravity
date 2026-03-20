<template>
  <div class="github-profile-page min-h-screen bg-[#000000] text-white selection:bg-white/20">
    <div v-if="!token" class="flex items-center justify-center min-h-screen p-6">
       <!-- GHP Token Entry -->
       <div class="w-full max-w-[440px] bg-zinc-950 border border-white/5 p-12 rounded-[40px] shadow-2xl relative overflow-hidden group">
          <div class="absolute -top-24 -right-24 w-48 h-48 bg-white/5 blur-[80px] rounded-full group-hover:bg-white/10 transition-colors duration-700"></div>
          <div class="relative z-10 space-y-10">
            <div class="flex flex-col items-center text-center space-y-6">
              <div class="w-20 h-20 bg-white rounded-[24px] flex items-center justify-center shadow-2xl ring-1 ring-white/20">
                <Github class="w-10 h-10 text-black" />
              </div>
              <div class="space-y-2">
                <h2 class="text-3xl font-black tracking-tight">GitHub SDK</h2>
                <p class="text-xs text-zinc-500 font-bold uppercase tracking-[0.4em]">Auth Protocol v1.0</p>
              </div>
            </div>

            <form @submit.prevent="saveToken" class="space-y-8">
              <div class="space-y-3">
                <label class="text-[10px] font-black text-zinc-600 uppercase tracking-[0.3em] ml-2">Personal Access Sequence</label>
                <input
                  v-model="inputToken"
                  type="password"
                  required
                  class="w-full bg-zinc-900/50 border border-white/5 rounded-2xl py-4.5 px-6 text-white placeholder-zinc-800 outline-none focus:border-white/20 transition-all font-mono text-sm tracking-widest"
                  placeholder="ghp_••••••••••••"
                />
              </div>
              <button 
                type="submit" 
                class="w-full py-5 bg-white text-black font-black text-xs uppercase tracking-[0.2em] rounded-2xl shadow-2xl hover:scale-[1.02] active:scale-[0.98] transition-all"
              >
                Authenticate Unit
              </button>
            </form>
          </div>
       </div>
    </div>

    <!-- Main ResendHub Interface -->
    <div v-else-if="profile" class="flex flex-col min-h-screen animate-in fade-in duration-1000">
      <!-- Top Management Bar -->
      <header class="h-20 border-b border-white/5 px-8 flex items-center justify-between sticky top-0 bg-black/80 backdrop-blur-xl z-50">
        <div class="flex items-center gap-6">
          <button @click="navigateBack" class="p-2.5 rounded-xl hover:bg-white/5 transition-colors text-zinc-500 hover:text-white">
            <ArrowLeft class="w-5 h-5" />
          </button>
          <div class="flex items-center gap-4 group cursor-pointer">
            <div class="w-9 h-9 bg-white rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg">
               <svg viewBox="0 0 24 24" class="w-6 h-6 text-black" fill="currentColor">
                 <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
               </svg>
            </div>
            <span class="text-xl font-black tracking-tighter">ResendHub</span>
          </div>
        </div>

        <div class="flex items-center gap-5">
           <button class="p-2.5 rounded-xl text-zinc-500 hover:text-white hover:bg-white/5 transition-all relative">
             <Bell class="w-5 h-5" />
             <span class="absolute top-2.5 right-2.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-black"></span>
           </button>
           <button @click="loadAll" class="p-2.5 rounded-xl text-zinc-500 hover:text-white hover:bg-white/5 transition-all" :class="{ 'animate-spin': loading }">
             <RefreshCw class="w-5 h-5" />
           </button>
           <button @click="logout" class="p-2.5 rounded-xl text-rose-500/50 hover:text-rose-500 hover:bg-rose-500/5 transition-all border border-rose-500/10">
             <LogOut class="w-5 h-5" />
           </button>
        </div>
      </header>

      <div class="flex-1 max-w-[1400px] mx-auto w-full px-8 py-12 grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-20">
        <!-- Profile Column -->
        <aside class="space-y-10 animate-in slide-in-from-left duration-700">
          <div class="relative w-full aspect-square rounded-full border-2 border-white/5 p-1.5 shadow-2xl">
             <img :src="profile.avatar_url" class="w-full h-full rounded-full object-cover filter brightness-90 contrast-110" />
          </div>
          
          <div class="space-y-4">
            <div>
              <h1 class="text-4xl font-black tracking-tighter text-white">{{ profile.name || profile.login }}</h1>
              <p class="text-lg text-zinc-500 font-medium tracking-tight">@{{ profile.login }}</p>
            </div>
            <p class="text-[13px] text-zinc-400 font-medium leading-relaxed">{{ profile.bio || 'I use Disk Utility PWA for my storage.' }}</p>
          </div>

          <button class="w-full py-3.5 bg-zinc-950 border border-white/10 rounded-2xl text-[11px] font-black uppercase tracking-[0.2em] shadow-lg hover:bg-white hover:text-black hover:border-white transition-all duration-300">
            Edit profile
          </button>

          <div class="flex items-center gap-6 text-[11px] font-bold text-zinc-500 uppercase tracking-widest border-t border-white/5 pt-8">
            <div class="flex items-center gap-2 group cursor-pointer">
              <Users class="w-3.5 h-3.5" />
              <span class="text-white group-hover:text-blue-400 transition-colors">{{ profile.followers }}</span> followers
            </div>
            <div class="flex items-center gap-2">
              <span class="text-white">{{ profile.following }}</span> following
            </div>
          </div>

          <div class="space-y-6 pt-2">
            <h3 class="text-[10px] font-black text-zinc-600 uppercase tracking-[0.4em]">Organizations</h3>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-zinc-950 border border-white/10 rounded-xl flex items-center justify-center text-[11px] font-black text-zinc-500 hover:text-white hover:border-white/30 cursor-pointer transition-all">OS</div>
              <div class="w-10 h-10 bg-zinc-950 border border-white/10 rounded-xl flex items-center justify-center text-[11px] font-black text-zinc-500 hover:text-white hover:border-white/30 cursor-pointer transition-all">UI</div>
            </div>
          </div>
        </aside>

        <!-- Repositories Content -->
        <div class="space-y-12">
          <!-- Animated Tab Navigation -->
          <nav class="flex items-center gap-10 border-b border-white/5 overflow-x-auto no-scrollbar">
            <div class="relative py-4">
               <button class="flex items-center gap-2.5 text-xs font-black uppercase tracking-widest text-white">
                 <BookOpen class="w-4 h-4" />
                 Overview
               </button>
               <div class="absolute bottom-0 left-0 right-0 h-1 bg-white rounded-t-full shadow-[0_-4px_12px_rgba(255,255,255,0.3)]"></div>
            </div>
            <button class="flex items-center gap-2.5 text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-white transition-colors py-4">
              <Database class="w-4 h-4" />
              Repositories
              <span class="px-2 py-0.5 bg-zinc-900 border border-white/5 rounded-full text-[9px] font-bold">{{ profile.public_repos }}</span>
            </button>
            <button class="flex items-center gap-2.5 text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-white transition-colors py-4">
              <Layout class="w-4 h-4" />
              Projects
            </button>
            <button class="flex items-center gap-2.5 text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-white transition-colors py-4">
              <Star class="w-4 h-4 text-zinc-600" />
              Stars
            </button>
          </nav>

          <!-- Pinned Grid -->
          <section class="space-y-8">
            <div class="flex items-center justify-between">
              <h3 class="text-[11px] font-black text-zinc-600 uppercase tracking-[0.4em]">Pinned</h3>
              <button class="text-[10px] font-bold text-zinc-600 hover:text-white transition-colors tracking-widest">Customize your pins</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Repo Card 1: Papi-hair-design style -->
              <div v-for="repo in topRepos" :key="repo.id" class="p-8 rounded-[32px] bg-zinc-950 border border-white/5 hover:border-white/20 hover:-translate-y-1.5 transition-all duration-500 group relative overflow-hidden h-full">
                <div class="absolute top-0 right-0 w-32 h-32 bg-white/5 blur-[50px] -mr-16 -mt-16 group-hover:bg-white/10 transition-colors"></div>
                <div class="relative z-10 flex flex-col h-full space-y-6">
                  <div class="flex items-center justify-between">
                    <h4 class="text-base font-black text-blue-400 group-hover:text-blue-300 transition-colors tracking-tight">{{ repo.name }}</h4>
                    <span class="px-2.5 py-1 bg-zinc-900 border border-white/10 rounded-full text-[9px] font-black text-zinc-500 uppercase tracking-widest">
                      {{ repo.private ? 'Private' : 'Public' }}
                    </span>
                  </div>
                  <p class="text-[13px] text-zinc-400 font-medium leading-relaxed line-clamp-2">{{ repo.description || 'Moderný systém pre prácu s API a monitoringom sietí.' }}</p>
                  
                  <div class="flex items-center gap-6 pt-4 text-[11px] font-bold text-zinc-500 uppercase tracking-widest mt-auto">
                    <div class="flex items-center gap-2">
                       <span class="w-3 h-3 rounded-full" :class="repo.language === 'TypeScript' ? 'bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.3)]' : 'bg-zinc-600'"></span>
                       {{ repo.language || 'Vanilla' }}
                    </div>
                    <div class="flex items-center gap-1.5 font-black">
                       <Star class="w-3.5 h-3.5" />
                       {{ repo.stargazers_count }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Contribution Matrix -->
          <section class="space-y-8 animate-in fade-in duration-1000 slide-in-from-bottom-5">
             <h3 class="text-[11px] font-black text-zinc-600 uppercase tracking-[0.4em]">1,432 contributions in the last year</h3>
             <div class="p-8 rounded-[40px] bg-zinc-950 border border-white/5 overflow-hidden shadow-2xl">
                <div class="flex gap-2 h-36 items-end">
                   <div v-for="w in 48" :key="w" class="flex-1 flex flex-col gap-2">
                      <div 
                        v-for="d in 7" 
                        :key="d" 
                        class="w-full aspect-square rounded-[3px] transition-all hover:scale-125 cursor-pointer"
                        :class="[
                          Math.random() > 0.8 ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.4)]' : 
                          Math.random() > 0.6 ? 'bg-emerald-700/60' : 
                          Math.random() > 0.3 ? 'bg-zinc-900' : 
                          'bg-zinc-950 border border-white/2'
                        ]"
                      ></div>
                   </div>
                </div>
             </div>
          </section>

          <!-- Detailed activity feed based on image -->
          <section class="space-y-12 pb-20">
             <h3 class="text-[11px] font-black text-zinc-600 uppercase tracking-[0.4em]">Recent activity</h3>
             
             <div class="flex gap-8 relative pb-12">
                <div class="absolute left-6 top-12 bottom-0 w-px bg-white/5"></div>
                
                <div class="relative z-10 w-12 h-12 rounded-full bg-zinc-950 border border-white/5 flex items-center justify-center text-emerald-400 shadow-xl self-start">
                   <CheckSquare class="w-5 h-5" />
                </div>
                
                <div class="space-y-6 flex-1 pt-1">
                   <div class="flex flex-col space-y-2">
                      <p class="text-sm font-medium text-zinc-300">
                        <span class="font-black text-white decoration-zinc-800 underline-offset-4 cursor-pointer hover:underline">janvyvojar</span> 
                        merged a pull request in 
                        <span class="font-black text-blue-400 hover:text-blue-300 cursor-pointer transition-colors">janvyvojar/resend-ui-clone</span>
                      </p>
                      <span class="text-[10px] font-black text-zinc-700 uppercase tracking-widest">2 days ago</span>
                   </div>

                   <!-- Actual Code Snippet from Image -->
                   <div class="rounded-[32px] bg-[#0A0A0A] border border-white/5 overflow-hidden shadow-2xl ring-1 ring-white/2 transition-all hover:ring-white/5 group">
                      <div class="px-6 py-4 border-b border-white/5 bg-zinc-900/40 flex items-center justify-between">
                         <div class="flex gap-2">
                            <div class="w-2.5 h-2.5 rounded-full bg-rose-500/30"></div>
                            <div class="w-2.5 h-2.5 rounded-full bg-amber-500/30"></div>
                            <div class="w-2.5 h-2.5 rounded-full bg-emerald-500/30"></div>
                         </div>
                         <span class="text-[9px] font-black text-zinc-700 tracking-[0.3em] uppercase group-hover:text-zinc-500 transition-colors">src/components/Button.css</span>
                      </div>
                      <div class="p-8 text-xs font-mono leading-relaxed bg-black/40">
                         <span class="text-slate-500 italic block mb-2">// Mirroring design from image.png</span>
                         <span class="text-white">.btn-primary {</span> <br/>
                         <span class="ml-6 text-zinc-400">background-color: <span class="text-blue-400">var(--color-white)</span>;</span><br/>
                         <span class="ml-6 text-zinc-400">color: <span class="text-blue-400">var(--color-black)</span>;</span><br/>
                         <span class="ml-6 text-zinc-400">transition: <span class="text-emerald-400">all var(--transition-fast)</span>;</span><br/>
                         <span class="text-white">}</span>
                      </div>
                   </div>
                </div>
             </div>
          </section>
        </div>
      </div>
    </div>

    <!-- Global Processing Overlay -->
    <transition enter-active-class="duration-700 ease-out" enter-from-class="opacity-0 scale-105" enter-to-class="opacity-100 scale-100">
      <div v-if="loading && profile" class="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] flex flex-col items-center justify-center gap-6">
        <div class="w-16 h-16 border-2 border-white/5 border-t-white rounded-full animate-spin"></div>
        <p class="text-[10px] font-black uppercase tracking-[0.6em] text-white/50 animate-pulse">Syncing ResendHub Assets</p>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { 
  Github, ArrowRight, ArrowLeft, LogOut, BookOpen, Database, 
  Layout, Star, Bell, RefreshCw, Users, CheckSquare 
} from 'lucide-vue-next';
import { useGithub } from '../composables/useGithub';

const { token, profile, repos, loading, error, setToken, logout: githubLogout, loadAll } = useGithub();

const inputToken = ref('');

const saveToken = async () => {
  setToken(inputToken.value);
  await loadAll();
};

const logout = () => {
  githubLogout();
};

const navigateBack = () => {
  window.history.back();
};

const topRepos = computed(() => {
  return repos.value.slice(0, 50).map(r => ({
    ...r,
    // Add fallback data for mock purposes if live data is sparse
    description: r.description || 'Premium repository part of the ResendHub ecosytem.'
  }));
});

onMounted(() => {
  if (token.value) {
    loadAll();
  }
});
</script>

<style scoped>
.github-profile-page {
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.1) transparent;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #000000;
}
::-webkit-scrollbar-thumb {
  background: #111111;
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: #222222;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;  
  overflow: hidden;
}

/* Specific text shadows and glows */
h1, h4 {
  text-shadow: 0 0 40px rgba(255, 255, 255, 0.1);
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
