import streamlit as st


def style_base_layout():
    
    st.markdown("""
                
                <style>
                
                    #MainMenu,header,footer{
                        # visibility:hidden;
                        }
                        
                    div[data-testid="stMainBlockContainer"]{
                        margin: 30px !important;
                        padding: 30px !important;
                    }
                </style>
                
                """,unsafe_allow_html=True)
    

def Login_screens_layout():
    st.markdown("""
    <style>
    
    .left-panel{
        background:linear-gradient(135deg,#f5f3ff,#ede9fe);
        padding:15px 10px;
        height:auto;
        border-radius: 10px;
    }

    .logo{
        font-size:25px;
        margin-bottom:5px;
        line-height: 1;
    }

    .heading{
        font-size:30px;
        font-weight:700;
        line-height:1.1;
        color:#0f172a;
        margin-bottom:10px;
    }

    .purple{
        color:#6d28d9;
    }

    .subtext{
        margin-top:2px;
        margin-bottom:8px;
        font-size:15px;
        color:#64748b;
    }

    .feature{
        display:flex;
        gap:6px;
        margin-top:9px;
        margin-bottom:9px;
        align-items:flex-start;
    }

    .feature-icon{
        width:32px;
        height:32px;
        border-radius:6px;
        background:#ede9fe;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:20px;
        flex-shrink:0;
    }

    .feature-title{
        font-weight:600;
        color:#0f172a;
        font-size:15px;
        margin: 0;
        line-height: 1;
    }

    .feature-desc{
        color:#64748b;
        font-size:13px;
        padding:2px;
        margin-top:1px;
        line-height: 1.2;
    }

    .signin{
        text-align:right;
        margin-bottom:8px;
        font-size:15px;
    }

    .form-title{
        font-size:25px;
        font-weight:700;
        color:#0f172a;
        margin-bottom:3px;
        padding:5px;
        line-height: 1;
    }

    .form-sub{
        color:#64748b;
        margin-bottom:15px;
        font-size:13px;
        padding:5px;
    }
    
    .footer{
        text-align:center;
        margin-top:15px;
        color:#64748b;
        font-size:12px;
    }
    
    
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        row-gap: 0 !important;
    }
    
        
    button[data-testid="stBaseButton-secondary"] {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    }
    

    </style>
    """, unsafe_allow_html=True)
    

def Signup_screens_layout():

    st.markdown("""
    <style>
    
    .left-panel{
        background:linear-gradient(135deg,#f5f3ff,#ede9fe);
        padding:15px 10px;
        height:auto;
        border-radius: 10px;
    }

    .logo{
        font-size:25px;
        margin-bottom:5px;
        line-height: 1;
    }

    .heading{
        font-size:30px;
        font-weight:700;
        line-height:1.1;
        color:#0f172a;
        margin-bottom:10px;
    }

    .purple{
        color:#6d28d9;
        margin-left:5px;
    }

    .subtext{
        margin-top:2px;
        margin-bottom:8px;
        font-size:15px;
        color:#64748b;
    }

    .feature{
        display:flex;
        gap:6px;
        margin-top:9px;
        margin-bottom:9px;
        align-items:flex-start;
    }

    .feature-icon{
        width:32px;
        height:32px;
        border-radius:6px;
        background:#ede9fe;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:20px;
        flex-shrink:0;
    }

    .feature-title{
        font-weight:600;
        color:#0f172a;
        font-size:15px;
        margin: 0;
        line-height: 1;
    }

    .feature-desc{
        color:#64748b;
        font-size:13px;
        padding:2px;
        margin-top:1px;
        line-height: 1.2;
    }

    .signin{
        text-align:right;
        margin-bottom:8px;
        font-size:15px;
    }

    .form-title{
        font-size:30px;
        font-weight:700;
        color:#0f172a;
        margin-bottom:3px;
        padding:5px;
        line-height: 1;
    }

    .form-sub{
        color:#64748b;
        margin-bottom:15px;
        font-size:18px;
        padding:5px;
    }
    
    .footer{
        text-align:center;
        margin-top:15px;
        color:#64748b;
        font-size:12px;
    }
    
    
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        row-gap: 0 !important;
    }
    
        
    button[data-testid="stBaseButton-secondary"] {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    }
    

    </style>
    """, unsafe_allow_html=True)