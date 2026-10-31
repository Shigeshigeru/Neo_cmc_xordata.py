##### **neo_cmc_xordata.py**
### **せつめいしょ**

ACANGで一部のゲームのMROMにCROMを暗号化した時の  
チェックサムが埋め込まれていないのでFBneoでCROMの  
スプライト展開時に化けてしまいます  

<img width="1189" height="939" alt="NEOGEO" src="https://github.com/user-attachments/assets/0c27c74a-a48e-4d79-984c-ecd687d51bdd" />
化け  

<img width="1189" height="942" alt="bakebake" src="https://github.com/user-attachments/assets/3cf4b806-c8d5-4427-a860-4277815fbea1" />
ゲームできません  



FBneo以外のエミュレータではそのチェックサムは無視されて  
実害はないのですが25年越しに謎を発見したIQ氏により  
FBneoには実装されてしまったのでMROMにチェックサムを  
埋め込まないとスプライトが化け化けでゲームができなくなります(´･д･`)  

参考サイト  
https://www.patreon.com/iq_132/posts/cracking-25-year-105172490  

そこでAIに頼み込んでチェックサムを埋め込むスクリプトを作成してもらいました！  
これでスプライトが化けません！やったぜ！  
だがしかし！完全逆変換とかではないので  
正規のCRCのファイルにはなりません残念( ´･ω･)  

### **対応ゲーム**
(自分が把握しているMROMにチェックサムが埋め込まれていないゲーム)  

**ザ・キング・オブ・ファイターズ’９９**  
**プレヒストリックアイル２　原始島**  
**ストライカーズ１９４５Ｐｌｕｓ**  

の三本です  

その他、bangbead、ganryu、garou、mslug3、nitd、sengoku3、zupapaに  
対応しているかもしれないみたいですがMROMが生データではない場合は  
実験に使うぐらいしかありません  
  
### **使い方**  
  
生データのMROMを用意します  
（MROMのバックアップを取ってから使用してください）  
  
**ザ・キング・オブ・ファイターズ’９９**の場合  
`python3 neo_cmc_xordata.py embed kof99_m1.bin kof99_m1_out.bin --game kof99  `
  
**プレヒストリックアイル２　原始島**の場合  
`python3 neo_cmc_xordata.py embed preisle2_m1.bin preisle2_m1_out.bin --game preisle2  `

**ストライカーズ１９４５Ｐｌｕｓ**の場合  
(書き込む部分にデータが入っているので--forceで上書き指定します)  
`python3 neo_cmc_xordata.py embed s1945p_m1.bin s1945p_m1_out.bin --game 1945p --force  `

他にも検証用のオプションがあるようですが基本的には  
使用しないので気にしなくてもいいです  

### **その他**    
CRC改変オプションはついていないのでご自身で改変おながいします  
MROMにチェックサムを埋め込む機能しかないので抽出バッチファイル等に  
組み込んで使用するといいと思われます  

思ったより変更部分が多くなったのですが化けないのでコレでいいと思います  
理屈上は８バイトの変更のみでいいような気がします  
もっと詳しく知りたい人はAIに聞いたりしてみたり  
FBneoのソースの[neo_decrypt.cpp](https://github.com/finalburnneo/FBNeo/blob/master/src/burn/drv/neogeo/neo_decrypt.cpp)のコードのじっくり眺めてみてください  
とりあえずゲームプレイしたいだけの方はコレでおｋです  

パブリックドメイン扱いにしますが商用利用等はヽ( ;´Д`)ﾉ ﾔﾒﾃｰ  

使用してなにかしら問題が起きた場合でも責任は負いません  
自己責任でおながいします  

自由に改変して使ってくださったほうがアテクシも浮かばれると思います  

糸冬
