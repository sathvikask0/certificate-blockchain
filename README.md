# certificate-blockchain

Tasks:

Test API's and functions (https://app.getpostman.com/join-team?invite_code=85949b4751d9d7e0b0312ee6f25c05cd&ws=de5c5fe0-3b5a-4644-8cbf-c4b5a27d124c)

Look for #..(TASK) comments in the code 


Points to remember: 

Make sure that our chain is upto date before sending certificates for verification (to find the right leader), and more importantly, while adding a new block (to add the block to the largest existing chain).
Add these functionalities to back-end (verify chain and resolve conflicts by calling the corresponding API's before submitting the certificates/adding a new block)

University keys:

U1:  "418a520d4e71e7cb6783bfc16e42dde2749cbb81d6dcac5b196db833818094dd"

U2:  "cd68875a5a7bf6943edf53d062b4d6ce8cea8e16a8167736bf077b6dd0f02bc2"

U3:  "72f397dc4e5c197e33a94397dcd95f1ff62912675b2d361ee3408e7783eb218c"

U4:  "d4f1dade285f4b60eb30088dbbf803d551caf3e39288b514a656e546b0def2f5"

Hash (SHA256) them and take [32:] to find the sender_id's (replace the addresses in self.nodes with them. Also use them in the 'sender' fields of the certificates for testing)



