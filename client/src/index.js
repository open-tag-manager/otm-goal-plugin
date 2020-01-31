import ContainerGoals from './pages/ContainerGoals'

export default () => {
  return {
    router (config) {
      const orgRoute = config.routes.find(element => element.name === 'Org')
      const containerRoute = orgRoute.children.find(element => element.name === 'Container')
      containerRoute.children.push({
        path: 'goals',
        name: 'Container-Goals',
        component: ContainerGoals
      })
    }
  }
}
