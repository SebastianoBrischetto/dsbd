<h1>Progetto DSBD UniCT 23/24 - Notifiche meteo </h1>
<h2>Setup</h2>
<h3>Autentificazione</h3>
associare chiave ssh ad account git => https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account <br />
generare chiave ssh => https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key <br />
nella pagina del repository cliccare su code, selezionare ssh e copiare la stringa <br />
usare il comando: git clone stringaCopiata <br />
<h3>Commitizen</h3>
se volete potete scaricare commitizen, una command utility per creare i commit secondo la convenzione => https://github.com/commitizen/cz-cli
<h3>Prima di pushare!!!</h3>
<ul>
<li>creare il proprio branch locale tramite: git branch nome/tipo_di_modifica/nome_modifica, <br />
ad esempio sebastiano/feat/microservizio_lista_citta.</li>
<li>commitare le modifiche su questo branch fino a che non si abbia finito</li>
<li>effettuare il push del branch online con: git push --set upstream origin nome/tipo_di_modifica/nome_modifica</li>
<li>aprire una pull request e assegnare tutti.</li>
</ul>
se possibile facciamo cosi in modo che prima di modificare/aggiungere codice tramite merge si possa dare un'occhiata da parte di tutti. 
<h2>Link Utili</h2>
docker engine => https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository <br />
docker desktop (opzionale) (richiede docker engine) => https://docs.docker.com/desktop/install/ubuntu/ <br />
bot telegram documentazione => https://docs.python-telegram-bot.org/en/v20.7/telegram.bot.html# <br />
