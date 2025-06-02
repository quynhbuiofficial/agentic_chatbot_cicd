import re
from langchain_neo4j import Neo4jGraph

def get_more_legal_information(text:str, kg: Neo4jGraph):
        print("\n----------- GET MORE: ",text[0] )
        # print('text::: ',text, ' lll: ', type(text))
        text = text[0]
        number_of_dieu = re.findall(r'điều\s+\d+', text)[0]
        number_of_khoan = re.findall(r'khoản\s+\d+', text)[0]
        cypher_query = f'MATCH (n: ĐIỀU {{name: "{number_of_dieu}"}})-[r]->(k:KHOẢN {{name:"{number_of_khoan}"}}) RETURN k.content'
        # print("1. cypher_query", cypher_query)
        results = kg.query(cypher_query)
        khoan_from_vsearch = results[0]['k.content']
        dieu_from_vsearch = number_of_dieu
         
        current_information_edit = khoan_from_vsearch
        
        # Xử lý logic để lấy thông tin trích dẫn bằng Cypher
        message_cypher_collected = ''
        cypher_query = f'MATCH (n:KHOẢN {{content:"{khoan_from_vsearch}"}}) RETURN n.name'
        # print("cypher_query1: ", cypher_query)
        results = kg.query(cypher_query.strip())
        # print('cypher_querycypher_querycypher_query: ', cypher_query, " results: ", results)
        if results: 
            khoan_name = results[0]['n.name']
            khoan_from_vsearch = khoan_from_vsearch.replace('*xuonghang*', '\n')
            message_cypher_collected += f'**Nội dung câu trả lời tại {dieu_from_vsearch} {khoan_name} Luật An Ninh Mạng 2018 như sau:**\n{khoan_from_vsearch}\n'
        else:
            khoan_name = ''
            message_cypher_collected += f'**Nội dung câu trả lời tại {dieu_from_vsearch} Luật An Ninh Mạng 2018 như sau:**\n{khoan_from_vsearch}\n'

        
        if "điều này" not in current_information_edit and "khoản này" not in current_information_edit and 'luật này' not in current_information_edit:     #Nếu trong Điều, Khoản trả lời không có tham chiếu return về trực tiếp ko cần chạy thêm query cypher khác
            return message_cypher_collected, khoan_name
        

        message_cypher_collected += '\n\n**Thông tin các trích dẫn khác:**\n\n'                    # Nếu trong Điều, Khoản trả lời có thông tin trích dẫ khác thì tiếp tục thực hiện cypher để truy vấn thêm. 
        # print('dieu_from_vsearch: ',dieu_from_vsearch)
        
        # dieu_name = dieu_from_vsearch.split('.')[0]
        dieu_name = dieu_from_vsearch
        info_dieunay = re.findall(r'quy định\s+(.*?)\s+điều này',current_information_edit)
        for item in info_dieunay:
            item_khoan = item
            khoan_lst = []
            diem_lst = []
            if 'khoản' in item_khoan:
                if 'và' in item_khoan:
                    item_khoan = item_khoan.replace(' và ', ', ') 
                if ',' in item:
                    item_khoan = item_khoan.replace(', ', ' khoản ')
                khoan_lst = re.findall(r'khoản\s\d+\b',item_khoan)
                khoan_lst = [re.sub(r'\s+', ' ', khoan).strip() for khoan in khoan_lst]
            
            item_diem = item
            # print("item_diem: ", item_diem)
            if 'điểm' in item_diem:
                if 'và' in item_diem:
                    item_diem = item_diem.replace(' và ', ', ')  
                if ',' in item_diem:
                    item_diem = item_diem.replace(', ', ' điểm ')
                diem_lst = re.findall(r'điểm\s[a-z]\b',item_diem)
                diem_lst = [re.sub(r'\s+', ' ', khoan).strip() for khoan in diem_lst]
                # print('diem_lst: ', diem_lst)

            cypher_query = ''
            for khoan_item in khoan_lst:
                if len(diem_lst) > 0:
                    for diem in diem_lst:
                        cypher_query = f"""
                                MATCH (n:ĐIỀU {{name:"{dieu_name}"}})-[:BAO_GỒM]->(n2:KHOẢN {{name:"{khoan_item}"}})-[:BAO_GỒM]->(n3:ĐIỂM {{name:"{diem}"}}) RETURN n3.content
                        """
                        cypher_query= cypher_query.strip()
                        # print('cypher_query1: ', cypher_query)
                        results = kg.query(cypher_query)
                        content = results[0]['n3.content']
                        message_cypher_collected += f'**Tại {diem} {khoan_item} {dieu_name} có quy định:**\n{content}\n'
                else:
                    cypher_query = f"""
                                    MATCH (n:ĐIỀU {{name:"{dieu_name}"}})-[:BAO_GỒM]->(n2:KHOẢN {{name:"{khoan_item}"}}) RETURN n2.content
                            """
                    cypher_query= cypher_query.strip()
                    results = kg.query(cypher_query)
                    # print('cypher_query2: ', cypher_query)
                    content = results[0]['n2.content']
                    message_cypher_collected += f'**Tại {khoan_item} {dieu_name} có quy định:**\n{content}\n'

        if 'luật này' in current_information_edit:
            lst_dieukhacs = re.findall(r'quy định\s+(.*?)\s+luật này',current_information_edit)
            # print('info_dieukhac: ', lst_dieukhacs)
            if lst_dieukhacs:
                for dieukhac in lst_dieukhacs:
                    # print('dieukhac', dieukhac)
                    if 'điều này' in dieukhac:
                        dieukhac = dieukhac.split('điều này')[1]
                    dieus_name_khac = re.findall(r'điều\s\d+\b', dieukhac)
                    # print('dieu_name: ', dieus_name_khac)
                    dieus_split = dieukhac.split('điều')
                    # print('dieus_split: ', dieus_split)
                    dieus_split = dieus_split[:-1]
                    # print('dieus_split', dieus_split)

                    for idx,item in enumerate(dieus_split):
                        # print('phanphanphan: ',item)
                        item_khoan = item
                        khoan_lst = []
                        diem_lst = []
                        if 'khoản' in item_khoan:
                            if 'và' in item_khoan:
                                    item_khoan = item_khoan.replace(' và ', ', ')
                            if ',' in item:
                                    item_khoan = item_khoan.replace(', ', ' khoản ')
                            khoan_lst = re.findall(r'khoản\s\d+\b',item_khoan)
                            # print(khoan_lst)
                    
                        item_diem = item
                        if 'điểm' in item_diem:
                            if 'và' in item_diem:
                                    item_diem = item_diem.replace(' và ', ', ')
                            if ',' in item_diem:
                                    item_diem = item_diem.replace(', ', ' điểm ')
                            diem_lst = re.findall(r'điểm\s[a-z]\b',item_diem)
                            # print(diem_lst)

                        cypher_query = ''
                        for khoan in khoan_lst:
                            if len(diem_lst) > 0:
                                for diem in diem_lst:
                                    cypher_query = f"""
                                            MATCH (n:ĐIỀU {{name:"{dieus_name_khac[idx]}"}})-[:BAO_GỒM]->(n2:KHOẢN {{name:"{khoan}"}})-[:BAO_GỒM]->(n3:ĐIỂM {{name:"{diem}"}}) RETURN n3.content
                                    """
                                    cypher_query= cypher_query.strip()
                                    results = kg.query(cypher_query)
                                    content = results[0]['n3.content']
                                    message_cypher_collected += f'**Tại {diem} {khoan} {dieus_name_khac[idx]} có quy định:**\n{content}\n'
                                    # print("DIEU KHAC1: ",cypher_query)
                            else:
                                cypher_query = f"""
                                                MATCH (n:ĐIỀU {{name:"{dieus_name_khac[idx]}"}})-[:BAO_GỒM]->(n2:KHOẢN {{name:"{khoan}"}}) RETURN n2.content
                                        """
                                cypher_query= cypher_query.strip()
                                results = kg.query(cypher_query)
                                content = results[0]['n2.content']
                                message_cypher_collected += f'**Tại {khoan} {dieus_name_khac[idx]} có quy định:**\n{content}\n'
                                # print("DIEU KHAC2: ",cypher_query)

        message_cypher_collected = message_cypher_collected.replace('*xuonghang*', '\n')
        return message_cypher_collected    