import React from 'react'
import {BrowserRouter as Router, Route, Switch, useHistory, useLocation} from 'react-router-dom'
import {Button, Container, Header, Input, List, Menu, Segment, Visibility,} from 'semantic-ui-react'
import {useQuery} from 'react-query'

import 'semantic-ui-less/semantic.less'


const menuStyle = {
  border: 'none',
  borderRadius: 0,
  boxShadow: 'none',
  marginBottom: '1em',
  marginTop: '4em',
  transition: 'box-shadow 0.5s ease, padding 0.5s ease',
}

const fixedMenuStyle = {
  border: '1px solid #5C5E33',
  boxShadow: '0px 3px 5px rgba(0, 0, 0, 0.2)',
}

const paragraphContentStyle = {
  margin: '1em',
}

const paragraphHeaderStyle = {
  fontSize: '1.2em',
  marginBottom: '0.8em',
}

const paragraphDescriptionStyle = {
  color: '#625D34',
}

const paragraphDescriptionHighLightStyle = {
  color: '#223523',
  fontWeight: 'bold',
}

function fetchParagraphs(key, query) {
  return fetch(`http://localhost:8000/apis/paragraphs?query=${query}`)
    .then(res => res.json())
}

export function useQueryParam(name) {
  const location = useLocation()
  return new URLSearchParams(location.search).get(name)
}

export function Index() {
  const history = useHistory()
  const query = useQueryParam('query')

  const [menuFixed, setMenuFixed] = React.useState(false)
  const [searchInput, setSearchInput] = React.useState('')

  const search = () => history.push(`/?query=${searchInput}`)

  const stickTopMenu = () => setMenuFixed(true)
  const unStickTopMenu = () => setMenuFixed(false)

  const {status, data, error} = useQuery(['paragraphs-query', query], fetchParagraphs)

  if (status === 'loading') {
    return <span>Loading...</span>
  }

  if (status === 'error') {
    return <span>Error: {error.message}</span>
  }

  const paragraphs = data.data

  return (
    <div>
      <Container text style={{marginTop: '2em'}}>
        <Header as='h1'>小說語句搜尋引擎</Header>
        <p>一個上傳小說文章和搜尋小說語句的平台</p>
      </Container>

      {/* Attaching the top menu is a simple operation, we only switch `fixed` prop and add another style if it has
            gone beyond the scope of visibility
          */}
      <Visibility
        onBottomPassed={stickTopMenu}
        onBottomVisible={unStickTopMenu}
        once={false}
      >
        <Menu
          borderless
          fixed={menuFixed ? 'top' : undefined}
          style={menuFixed ? fixedMenuStyle : menuStyle}
        >
          <Container text>
            <Menu.Item style={{flex: '2 2 auto', paddingLeft: '0.5em'}}>
              <Input
                action={{content: '搜尋', onClick: search}}
                onChange={(_, data) => setSearchInput(data.value)}
                placeholder='Search...'
              />
            </Menu.Item>
            <Menu.Item style={{flex: '1 1 auto'}}/>
            <Menu.Item style={{flex: '0 0 auto'}} position='right'>
              <Button>上傳文章</Button>
            </Menu.Item>
          </Container>
        </Menu>
      </Visibility>

      <Container text>
        <List divided relaxed>
          {
            paragraphs.length > 0 ? paragraphs.map(paragraph => (
              <List.Item key={paragraph.id}>
                <List.Content style={paragraphContentStyle}>
                  <List.Header style={paragraphHeaderStyle}>{paragraph.articleTitle}</List.Header>
                  <List.Description style={paragraphDescriptionStyle}>{
                    paragraph.content
                      .split(query)
                      .map((part, i) => (i === 0) ? (<span>{part}</span>) :
                        <span><span style={paragraphDescriptionHighLightStyle}>{query}</span>{part}</span>)
                  }</List.Description>
                </List.Content>
              </List.Item>
            )) : <span>沒有搜尋到任何結果</span>
          }
        </List>
      </Container>

      <Segment inverted style={{backgroundColor: '#494A28', margin: '5em 0em 0em', padding: '1em 0em'}} vertical>
        <Container textAlign='center'>
          <List horizontal inverted divided link size='small'>
            <List.Item>
              2020 兩大類
            </List.Item>
          </List>
        </Container>
      </Segment>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <Switch>
        <Route path='/'>
          <Index/>
        </Route>
      </Switch>
    </Router>
  )
}
