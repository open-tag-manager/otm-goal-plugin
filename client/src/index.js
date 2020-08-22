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
    },
    app (app) {
      app.$store.dispatch('addContainerMenu', {label: 'Goal', name: 'Container-Goals'})
      app.$store.dispatch('addTableAction', {label: 'Set goal', name: 'Container-Goals'})
      app.$store.dispatch('addEventTableAction', {label: 'Set goal', name: 'Container-Goals'})
    }
  }
}
