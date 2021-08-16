import streamlit as st


def render_technical_paper():
    r'''
    # Technical design
    # 1. Overview

    The Credix marketplace is built upon of the following concepts (& contracts):

    - **Reserve pool**
    Allows investors to stake USDC and earn yield before being allocated to the liquidity pool
    - **Deals**
    Represents a deal and its characteristics
    - **Repayment pool**
    Collects the repayments (interest + principal) of the borrowers
    - **Match making mechanism**
    Orchestrates the sale of investor tokens to provide liquidity

    The protocol is fuelled by the following tokens:

    - **Reserve Token (RT) -** A non-fungible token (NFT) representing the investor's stake in the reserve
    - **Underwriter Token (UT) -** A non-fungible token (NFT) representing the underwriter's stake in the junior tranche of a specific deal
    - **Investor Token (IT) - t**oken provided to liquidity providers reflecting the net asset value of the liquidity pool
    - **Credix Token (CRED)** - token used for governance and rewards

    # 2. Main Concepts

    ## 2.1. Reserve Pool

    Most DeFi protocols provide liquidity by introducing a reserve as part of their liquidity pools. Some cap this reserve (e.g. Centrifuge) whilst other's keep it dynamic and let its size be determined by market making mechanisms (e.g. Compound). Both solutions have a negative impact on the investors' yield as the reserve's capital is not deployed.

    The reserve pool as introduced by Credix is a novel way of providing liquidity without compromising on investors' yield. This is achieved by decoupling the reserve from the liquidity pool itself. Leveraging DeFi's composability, this isolated reserve still generates yield by connecting it to other protocols (e.g. Compound).

    How does this work in practice? Let's illustrate by example. Let's say you're an investor and want to put your capital to work by investing in Credix. As an investor, you cannot invest in individual deals on the platform; this is only possible as an underwriter, more on that later. The steps you will take are the following:

    1. You deposit USDC in the Credix Reserve
    2. In exchange for this investment, you get a Reserve Token representing your share. Each issued RT stores:
        - the USDC amount
        - the date and time of issuance
    3. The deposited USDC is automatically put into e.g. the Compound Protocol to generate yield
    4. At any point in time, you can withdraw your RT's and receive your original USDC investment + generated yield to that point in time. Upon withdrawal, Credix takes a 10% performance fee.

    ## 2.2. Deals

    ### 2.2.1. Characteristics

    A deal represents a single credit line of one of the borrowers. Each deal is captured in a contract defined by the following characteristics:

    ---

    **Principal**
    The total amount of the credit line in USDC
    *e.g. USDC 1.000.000*

    **Financing fee**
    The percentage of the principal (= sur plus) that has to be repaid as interest
    *e.g. 15% (⇒ total interest = USDC 150.000)*

    **Leverage ratio**
    The ratio of the size of the senior tranche over the junior tranche
    *e.g. 4 ⇒ For every 4 parts senior tranche, there is 1 part junior tranche (= 80% senior, 20% junior)*

    **Underwriter fee**
    The percentage taken by the underwriters on the repaid interest to the investors. Acts as a reward for taking more risk
    *e.g. 20%*

    **Time to maturity**
    The number of months after which the principal has to be repaid
    *e.g. 12 months*

    **Repayment schedule**
    The rate at which the repayments have to be done
    *e.g. monthly*

    ---

    ### 2.2.2. Junior and senior tranche

    Each deal consists of a junior tranche and a senior tranche. The exact composition is determined by the leverage ratio. If we take a leverage ratio of 4, we will have 20% junior tranche and 80% senior tranche.

    The senior tranche consists of capital provided by the investors. Investors don't allocate their USDC on a per-deal basis. Instead, they invest in Investor Tokens (IT's). The IT price reflects the gained capital (= interest payments) of all deals. Investors can expect a lower risk, stable yield (as they are protected from first losses by the underwriters). Their expected yield is given by:

    $$investor\ yield = financing\ fee * (1 - credix\ fee - underwriter\ fee)$$

    The junior tranche consists of 'first loss capital' and is provided by the underwriters. As the name "first loss capital" suggests, the underwriters face losses first when a borrower is unable to repay its interest or principal. Therefore, underwriters will only underwrite a deal after they have thoroughly analysed its details (= borrowers' previous bank statements, balance sheet etc). This higher risk also comes with a reward: if all repayments are made successfully, the underwriters will receive a performance fee (= underwriter fee) represented by a percentage of the repaid interest to the investors. The higher the leverage ratio, the higher the yield of the underwriters will be. Their expected yield is given by:

    $$underwriter\ yield = \\ interest\ rate * (1 - credix\ fee + leverage\ ratio*underwriter\ fee)$$

    The credix fee will be 10% and is taken at the very last step (after the investor's and underwriter's yield is paid out). This fee will be used to fund development, developer grants, community building, etc.

    ### 2.2.3. New deal

    What happens when a new deal arrives on the Credix marketplace?

    1. The deal's details are stored in a new deal contract
    2. Underwriters can now stake USDC in the junior tranche of the deal contract & get an underwriter token (UT) in return. The underwriter token stores:
        - A reference to the deal
        - The amount of USDC staked
    3. Once the junior tranche is fully funded, the senior tranche of the deal is automatically filled by the capital available in the repayment pool (= repaid principals + interest repayments of previous deals). This behaviour ensures that the available capital is active on a quasi-continuous basis.
    4. If there is not enough capital available in the repayment pool to fund the senior tranche of the new deal, the reserve pool is activated. Those investors which hold the oldest Reserve Tokens (RT's) now get the opportunity to enter the Credix protocol and earn stable yield. The process goes as follows:
        1. The oldest RT's are selected
        2. The selected RT's USDC-equivalent + yield is withdrawn from Compound (or any other yield-generating protocol)
        3. The RT's yield is transferred to the investor's wallet
        4. The RT's USDC-equivalent is exchanged for n Investor Tokens (IT's) at the current IT price:

            $n_{IT} = \frac{RT_{USDCequivalent}}{price_{IT}}$

            where:

            $price_{IT} = \frac{1 + repaid\ interest + repaid\ principals +outstanding\ credit}{n_{IT}}$

        5. The selected RT's are burned
    5. Non-selected investors keep their RT's and continue earning interest. Their RT's age, giving them priority when the next deal comes

    ## 2.3. Repayments

    ### 2.3.1. Borrower interest payments

    On a periodical basis, the borrower is expected to do an interest payment. The following steps are performed:

    1. Borrower sends the interest payments (USDC) to the respective deal contract
    2. Deal contract checks if the payment complies with the terms (amount, timing, etc)
    3. A 10% Credix fee is send to the Credix wallet
    4. Deal contract sends the investor's cut of the interest payment to the repayment contract.
    5. Deal contract sends the underwriter's cut of the interest payment to the underwriters' wallets

    ### 2.3.2. Borrower principal repayment

    At the time of maturity, the borrower is expected to repay the principal. The following steps are performed:

    1. Borrower sends the principal repayment (USDC) to the respective deal contract
    2. The deal contract checks the total amount of interest payments made to the repayment contract. It compares this amount with the expected yield for the senior tranche and takes the difference from the principal and sends this difference + the initial senior-tranche's USDC value to the repayment contract. This behaviour ensures the stable yield for the investors, even if there have been non-payments along the deal's lifecycle.
    3. The remainder of the capital flows back to the underwriters. If no defaults have happened, the underwriters can expect the 'underwriter yield' as outlined above.

    ## 2.4. Matchmaking & liquidity

    As explained before, Credix deploys a new kind of reserve. Of course, liquidity is of uttermost importance to maintain a healthy DeFi protocol. In Credix, the matchmaking contract enables liquidity in the following way:

    1. The selling Investor sends the amount of IT's he/she wants to redeem to the match making contract
    2. The match making contract checks if there are enough funds are available in the reserve pool
        1. **If there is enough liquidity in the reserve pool**
            - Call the Reserve Pool and select the buying investors with oldest RT's
            - The number of RT's equal to the value of selling investors' IT's are burned, the USDC amount is redeemed from compound and send to selling investor's wallet. The generated yield is send to the buying investor's wallet
            - The buying investor's IT balance increases accordingly
        2. **If there is not enough liquidity in the reserve pool**
            - Perform a. for the available funds in the reserve pool
            - Fund from the repayment pool: the selling investor's IT's are burned and he/she receives the USDC amount at the current IT price. The repayment pool's value reduces with this USDC amount, keeping the IT price constant.

    # 3. Token structure

    ## 3.1. **Token types**

    - **Reserve Token (RT) -** A non-fungible token (NFT) representing the investor's stake in the reserve
    - **Underwriter Token (UT) -** A non-fungible token (NFT) representing the underwriter's stake in the junior tranche of a specific deal
    - **Investor Token (IT) - t**oken provided to liquidity providers reflecting the net asset value of the liquidity pool
    - **Credix Token (CRED)** - token used for governance and rewards

    ## 3.2. **Token flows**

    Our pool is implemented as a common two-tiered structure. This is often called an A/B tranche or junior/senior tranche structure. In this tiered investment structure, our investors do not share all risks and returns pro rata. Our returns are distributed via a waterfall structure. This means that losses/defaults are allocated from bottom to top. Meaning that underwriters take losses first. The investors are prioritized when receive their investment back and have a fixed return. The remaining proceeds all flow to the Underwriters.

    Let's explain the token flow by example. Let's say we have a deal with deal size 1M USDC with a leverage ratio of 4x (200k USDC investment in the junior tranche by the underwriter and 800k USDC investment in the senior tranche by the investors). Upon maturity, the interests will have accrued to a total of 150k USDC (if we assume an interest rate of 15%)*. Let's investigate the payout of the interest to the investors, underwriters and Credix step by step:
    '''

    st.image("technical_design_token_flows.png")

    '''
    1. The Credix fee (10%) is taken
    2. The investors can expect a yield of 10.5%, given by:
    
        $investor\ yield = interest\ rate * (1 - bridge\ fee - underwriter\ fee)$
        
        In other words, the investors can expect the interest rate to be discounted by the bridge fee and the underwriter fee. The investors are the first to be paid out and thus bear the least amount of risk. 
    
    3. If no defaults occur, the underwriters can expect a yield of 25.5%, given by:
    
        $underwriter\ yield = \\ interest\ rate * (1 - credix\ fee + leverage\ ratio*underwriter\ fee)$
        $underwriter\ yield = 0.15*(1-0.1+4*0.2) =0.255$
    
        In other words, the Underwriters can expect the interest rate plus the underwriting fee, weighted by the leverage in the deal. 
    
    **Interests are paid on a monthly basis, but this has no effect on the example.*  
    '''